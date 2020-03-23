from lime.discretize import QuartileDiscretizer
import lime
import lime.lime_tabular
import pandas as pd
import pickle as pk
import traceback

class LimeReport:
    """
    LimeReport is used to analyse the model prediction.
    :param _data_sample_tobe_analysed: Numpy array of samples to be analysed.
    :type _data_sample_tobe_analysed: numpy
    :param _training_data_file_name: File name of data used for model training.
    :type _training_data_file_name: str
    :param _normalized_training_data_file_name: File name of normalised data used for model training.
    :type _normalized_training_data_file_name: str
    :param _model_pickle_file_name: Pickle file name of the model.
    :type _model_pickle_file_name: str
    :param _categorical_features: Columns-name of categorical type.
    :type _categorical_features: list
    :param _training_data_panda_frame: Panda frame used locally.
    :type _training_data_panda_frame: Pandas Dataframe
    :param _normalized_training_data_panda_frame: Panda frame used internally.
    :type _normalized_training_data_panda_frame: Pandas Dataframe
    :param _predict_function: Lambda function used internally.
    :type _predict_function: function
    :param _lime_explainer: Lime explainer object used internally.
    :type _lime_explainer: object
    :param _training_data_quartile_details: Numpy array used internally.
    :type _training_data_quartile_details: numpy
    :param _norm_training_data_quartile_details: Numpy array used internally.
    :type _norm_training_data_quartile_details: numpy
    :param _output_file: file name used to store Lime results.
    :type _output_file: str
                
    """
    # array of samples, should be directly consumable for prediction, n*m
    # n=number of samples, m=features in each sample
    _data_sample_tobe_analysed = None
    # Raw data file, having only relevant features used for training
    _training_data_file_name = None
    # Normalized raw data file, having only relevant features used for training
    _normalized_training_data_file_name = None
    _model_pickle_file_name = None
    # List of categorical features used in training
    _categorical_features = None
    _training_data_panda_frame = None
    _normalized_training_data_panda_frame = None
    _predict_function = None
    _lime_explainer = None
    _training_data_quartile_details = None
    _norm_training_data_quartile_details = None
    _output_file = None

    def __init__(self, _data_sample_to_be_analysed, _training_data_file_name, _normalized_training_data_file_name,
                 _model_pickle_file_name, _categorical_features, _output_file):
        self._data_sample_tobe_analysed = _data_sample_to_be_analysed
        self._training_data_file_name = _training_data_file_name
        self._normalized_training_data_file_name = _normalized_training_data_file_name
        self._model_pickle_file_name = _model_pickle_file_name
        self._categorical_features = _categorical_features
        self._output_file = _output_file
        self._file_loader()

    def _file_loader(self):
        """
        _file_loader, internal method used for Lime data preparation
        
        """
        try:
            self._training_data_panda_frame = pd.read_csv(self._training_data_file_name)
            self._normalized_training_data_panda_frame = pd.read_csv(self._normalized_training_data_file_name)
            model = pk.load(open(self._model_pickle_file_name, 'rb'))
            self._predict_function = lambda x: model.predict_proba(x).astype('float')
            self._lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                self._normalized_training_data_panda_frame.values,
                feature_names=list(self._normalized_training_data_panda_frame.columns),
                class_names=['0', '1'],
                categorical_features=self._categorical_features,
                categorical_names=self._categorical_features,
                kernel_width=3)
            training_data_quartile = QuartileDiscretizer(self._training_data_panda_frame.values,
                                                         self._categorical_features,
                                                         self._training_data_panda_frame.columns,
                                                         labels=None)
            self._training_data_quartile_details = training_data_quartile.names
            self._norm_training_data_quartile_details = self._lime_explainer.discretizer.names
        except Exception as e:
            traceback.print_stack()
            print(e)

    def lime_analysis(self):
        """
        lime_analysis, method used to run Lime analysis.
        :return: list of lime explanations
        :rtype: list
        """
        try:
            lime_report = []
            output_pd = pd.read_csv(self._output_file)
            col_count = output_pd.shape[1]
            for column in self._normalized_training_data_panda_frame.columns:
                col_name = "LIME_" + column
                output_pd[col_name] = None

            for i in range(len(self._data_sample_tobe_analysed)):
                print(i)
                ith_data_sample = self._data_sample_tobe_analysed[i].reshape(-1)
                lime_explanation = self._lime_explainer.explain_instance(ith_data_sample, self._predict_function,
                                                                         num_features=self._training_data_panda_frame.shape[1])
                pdFrame = self._data_mapper(lime_explanation, i, output_pd, col_count)
                lime_report.append(pdFrame.values)
            output_pd.to_csv(self._output_file)
            return lime_report
        except Exception as e:
            print(e)
            traceback.print_stack()

    def _data_mapper(self, lime_explanation, ith_index, output_data_frame, col_count):
        """
        _data_mapper, internal method used for Lime report preparation.
        :param lime_explanation: object of lime class
        :type lime_explanation: object
        :param ith_index: index
        :type ith_index: int
        :param output_data_frame: dataframe used to store output of Lime results
        :type output_data_frame: Pandas DataFrame
        :param col_count: number of columns in output_pd variable of calling method
        :type col_count: int
        :return: output dataframe
        :rtype: Pandas Dataframe
        """
        try:
            pd_data_frame = pd.DataFrame(columns=['FeatureIndex', 'Quartile_Block', 'Coef'], index=[])

            lime_result_details = lime_explanation.as_list()
            lime_result_details_sorted = lime_explanation.local_exp
            if 1 in lime_result_details_sorted:
                lime_result_temp = lime_result_details_sorted[1]
                for i in range(len(lime_result_temp)):
                    feature_index = lime_result_temp[i][0]
                    quartile_feature_tobe_searched = lime_result_details[i][0]
                    quartile_feature_index = self._norm_training_data_quartile_details[feature_index].index(quartile_feature_tobe_searched)
                    quartile_feature = self._training_data_quartile_details[feature_index][quartile_feature_index]
                    pd_data_frame.loc[i] = [feature_index, quartile_feature, lime_result_temp[i][1]]
                    output_data_frame.iloc[ith_index, col_count + feature_index] = lime_result_temp[i][1]
                return pd_data_frame

            # print("Returning None")
            return None
        except Exception as e:
            traceback.print_stack()
            print(e)
