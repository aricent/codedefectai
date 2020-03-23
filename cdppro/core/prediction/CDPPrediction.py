import pickle
import traceback
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from prediction import Constants as constants
from prediction import LimeReport as LimeReport
from prediction.Constants import Springboot, OpenCV, CoreFx


class CDPPrediction:
    """ 
    CDPPrediction is used for data prepration and model prediction.
    :param  _project_ID: Unique ID of the project
    :type  _project_ID: str
    :param  _trained_model_pickel_filename: Pickle file name of the trained model
    :type  _trained_model_pickel_filename: str
    :param  _PCA_pickle_filename: Pickle file name of the PCA model, if applicable.
    :type  _PCA_pickle_filename: str
    :param  _min_max_scaler_filename: Pickle file name of the MinMaxScaler model.
    :type  _min_max_scaler_filename: str
    :param  _imputer_pickle_filename: Pickle file name of the Imputer model.
    :type  _imputer_pickle_filename: str
    :param  _is_PCA_required: Flag used, if PCA is required or not.
    :type  _is_PCA_required: Bool
    :param  _input_data_filename: File name whose data has to be predicted.
    :type  _input_data_filename: str
    :param  _data_for_model: Numpy used for data collection
    :type  _data_for_model: numpy
    :param  _data_DF: PandaFrame used for data collection.
    :type  _data_DF: Pandas Dataframe
    :param  _columns_to_be_dropped: Columns-name to be dropped.
    :type  _columns_to_be_dropped: list
    :param  _columns_to_be_one_hot_encoded: Columns-name to be one hot encoded.
    :type  _columns_to_be_one_hot_encoded: list
    :param  _categorical_coulmns: Columns-name of categorical type.
    :type  _categorical_coulmns:list
    :param  _scaled_input_file_name: File name used to save normalised data.
    :type  _scaled_input_file_name: str
    :param  _files_type_tobe_processed: Files extension to be analysed.
    :type  _files_type_tobe_processed: list
    :param  _threshold_val: Threshold value for model prediction.
    :type  _threshold_val: float
    
    """
    _project_ID = None
    _trained_model_pickel_filename = None
    _PCA_pickle_filename = None
    _min_max_scaler_filename = None
    _imputer_pickle_filename = None
    _is_PCA_required = False
    _input_data_filename = None
    _data_for_model = None
    _data_DF = None
    _columns_to_be_dropped = None
    _columns_to_be_one_hot_encoded = None
    _categorical_coulmns = None
    _scaled_input_file_name = None
    _files_type_tobe_processed = None
    _threshold_val = 0.5

    def __init__(self, project_id, files_type_to_be_processed, model_pickle_file,
                 pca_pickle_file_name, min_max_scaler_pickle_file_name,
                 imputer_pickle_file_name, columns_to_be_dropped, columns_to_be_one_hot_encoded,
                 categorical_coulmns, is_pca_required, is_ohe_required,
                 input_data_file_name, _output_file, _scaled_input_file_name, _threshold_val):
        self._project_ID = project_id
        self._trained_model_pickel_filename = model_pickle_file
        self._PCA_pickle_filename = pca_pickle_file_name
        self._imputer_pickle_filename = imputer_pickle_file_name
        self._is_PCA_required = is_pca_required
        self._is_OHE_required = is_ohe_required
        self._input_data_filename = input_data_file_name
        self._min_max_scaler_filename = min_max_scaler_pickle_file_name
        self._output_file = _output_file
        self._columns_to_be_dropped = columns_to_be_dropped
        self._categorical_coulmns = categorical_coulmns
        self._columns_to_be_one_hot_encoded = columns_to_be_one_hot_encoded
        self._scaled_input_file_name = _scaled_input_file_name
        self._files_type_tobe_processed = files_type_to_be_processed
        self._threshold_val = _threshold_val

        if (self._trained_model_pickel_filename is None) or (self._input_data_filename is None) or (
                self._is_PCA_required and (self._PCA_pickle_filename is None)):
            raise Exception("Data members are not initialized properly")

    def __normalized_data_scale(self, data_frame):
        """ 
        __normalized_data_scale, internal method used for data normalization.
        :param data_frame: PandaFrame that will be normalized.
        :type data_frame: Pandas dataframe
        
        :return :  A normalized panda frame.
        :rtype : Pandas Dataframe

        """
        try:
            imputer = pickle.load(open(self._imputer_pickle_filename, 'rb'))
            temp_data = imputer.transform(data_frame)

            minmaxScaler = pickle.load(open(self._min_max_scaler_filename, 'rb'))
            temp_data = minmaxScaler.transform(temp_data)
            normalized_df = pd.DataFrame(data=temp_data[0:, 0:], columns=data_frame.columns)
            normalized_df = normalized_df.clip(-1, 1)

            return normalized_df
        except Exception as ex:
            print(ex)
            traceback.print_stack()

    def __one_hot_encoding_integration(self, data_frame_to_be_normalized):
        """
        __one_hot_encoding_integration, internal method used for OneHot Encoding.
        
        :param data_frame_to_be_normalized: PandaFrame that will be OneHot Encoded.
        :type data_frame_to_be_normalized: Pandas Dataframe
        
        """
        try:
            temp_df = data_frame_to_be_normalized.copy(deep=True)
            temp_df = temp_df.drop(columns=self._columns_to_be_one_hot_encoded)
            self._data_for_model = temp_df.values[:, :temp_df.shape[1]]
            onehotEncoderForAuthor = OneHotEncoder(sparse=False, categories=[range(20)])
            onehotEncoderForStatus = OneHotEncoder(sparse=False, categories=[(['A', 'D', 'M', 'R'])])

            for column in self._columns_to_be_one_hot_encoded:
                if column in data_frame_to_be_normalized.columns:
                    column_data = data_frame_to_be_normalized[column]
                    one_hot_encoded_data = None
                    if 'AUTHOR_NAME_ENCODED' == column:
                        one_hot_encoded_data = onehotEncoderForAuthor.fit_transform(column_data.values.reshape(-1, 1))
                    elif 'FILE_STATUS' == column:
                        one_hot_encoded_data = onehotEncoderForStatus.fit_transform(column_data.values.reshape(-1, 1))
                    else:
                        # ToBe decided based upon the other features.
                        continue
                    self._data_for_model = np.concatenate((self._data_for_model, one_hot_encoded_data), axis=1)
        except Exception as ex:
            print(ex)
            traceback.print_stack()

    def __pca_integration(self):
        """
        __pca_integration, internal method used for PCA
        
        """
        
        try:
            pcaModel = pickle.load(open(self._PCA_pickle_filename, 'rb'))
            self._data_for_model = pcaModel.transform(self._data_for_model)
        except Exception as ex:
            print(ex)
            traceback.print_stack()

    
    def prepare_data_for_model(self):
        """
        prepare_data_for_model, external method used for preprocessing the data.
        Internally it will call all internal methods for data preparation.
        
        """
        try:
            file_status = None
            raw_data = pd.read_csv(self._input_data_filename)
            raw_data = raw_data.reindex(sorted(raw_data.columns), axis=1)

            raw_data = raw_data[raw_data['FILE_NAME'].str.endswith(self._files_type_tobe_processed)]
            self._data_DF = raw_data.copy(deep=True)
            if 'FILE_STATUS' in raw_data.columns:
                file_status = raw_data['FILE_STATUS']

            raw_data = raw_data.drop(columns=self._columns_to_be_dropped)

            # Method call for normalized the data.
            normalized_df = self.__normalized_data_scale(raw_data)
            column_list = np.append(raw_data.columns.values,['FILE_ADDED','FILE_DELETED','FILE_MODIFIED','FILE_RENAMED'])

            if file_status is not None:
                normalized_df['FILE_STATUS'] = file_status.values

            # Saving Intermediate file
            normalized_df.to_csv(self._scaled_input_file_name, index=False)
            self._data_for_model = normalized_df.values

            if self._is_OHE_required:
                self.__one_hot_encoding_integration(normalized_df)

            if self._is_PCA_required:
                self.__pca_integration()
                
			# Saving Intermediate file
            raw_data = pd.DataFrame(data=self._data_for_model[0:,0:], columns=column_list)  
            raw_data.to_csv(self._scaled_input_file_name, index=False)

        except Exception as ex:
            print(ex)
            traceback.print_stack()

    def predict(self):
        """
        predict, external method used for prediction.
        :return: Prediction Dataframe
        :rtype: Pandas Dataframe
        """
        try:
            # Load Pickle file generated using with PCA data
            model = pickle.load(open(self._trained_model_pickel_filename, 'rb'))
            if model is not None:
                model_prediction = model.predict(self._data_for_model)
                predictProba = model.predict_proba(self._data_for_model)

                # prediction = (predictProba[:, 1] >= 0.6).astype('int')

                prediction = pd.DataFrame(predictProba[:, 1] >= self._threshold_val).astype('int')

                higherProba = []
                for i in range(predictProba.shape[0]):
                    if predictProba[i][1] > predictProba[i][0]:
                        higherProba.append(predictProba[i][1])
                    else:
                        higherProba.append(predictProba[i][0])

                self._data_DF['Prediction'] = prediction
                self._data_DF['Confidence'] = higherProba
                self._data_DF.to_csv(self._output_file, index=False)

                return prediction
        except Exception as ex:
            print(ex)
            traceback.print_stack()


if __name__ == '__main__':

    try:
        project_id = constants.OPENCV_ID
        project_obj = None
        if constants.SPRINGBOOT_ID == project_id:
            project_obj = Springboot()
        elif constants.OPENCV_ID == project_id:
            project_obj = OpenCV()
        elif constants.COREFX_ID == project_id:
            project_obj = CoreFx()
        else:
            print("Wrong Project Id Provided...")

        if project_obj is not None:
            obj = CDPPrediction(project_id,
                                project_obj.FILE_TYPE_TO_BE_PROCESSED,
                                project_obj.MODEL_PICKLE_FILE_NAME,
                                project_obj.PCA_PICKLE_FILE_NAME,
                                project_obj.MIN_MAX_SCALER_PICKLE_FILE_NAME,
                                project_obj.IMPUTER_PICKLE_FILE_NAME,
                                project_obj.COLUMNS_TO_BE_DROPPED,
                                project_obj.COLUMNS_TO_BE_ONE_HOT_ENCODED,
                                project_obj.CATEGORICAL_COLUMNS,
                                project_obj.PCA_REQUIRED,
                                project_obj.ONE_HOT_ENCODING_REQUIRED,
                                project_obj.RAW_CDP_FILE_NAME,
                                project_obj.OUTPUT_FILE,
                                project_obj.SCALED_INPUT_FILE_NAME,
                                project_obj.THRESHOLD)

            obj.prepare_data_for_model()

            _prediction = obj.predict()

            validationData = pd.read_csv(project_obj.SCALED_INPUT_FILE_NAME)

            # For list of items
            sample_count = validationData.shape[0]
            data_tobe_analysed = validationData.values[:sample_count].reshape(sample_count, -1)
            # for testing individual item
            # data_tobe_analysed = validationData.values[535].reshape(1,-1)
            lr = LimeReport(data_tobe_analysed,
                            project_obj.RAW_TRAINING_DATA_FILE_NAME,
                            project_obj.SCALED_TRAINING_DATA_FILE_NAME,
                            project_obj.MODEL_PICKLE_FILE_NAME,
                            project_obj.CATEGORICAL_COLUMNS,
                            project_obj.OUTPUT_FILE
                            )

            out = lr.lime_analysis()

    except Exception as e:
        print(e)
