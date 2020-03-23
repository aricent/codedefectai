import ast
import os
import time
from datetime import datetime, timedelta

import pandas as pd

from prediction import Constants as constants
from prediction.CDPPrediction import CDPPrediction
from DataBaseAccess.InsertPredictedDataInDB import InsertPredictedDataInDB
from DataBaseAccess.RawGitDataInDB import RawGitDataInDB
from DataExtraction.GetCommitAndIssueDetails import PrepareCommitsIssuesDataForPrediction
from prediction.LimeReport import LimeReport
from Preprocessing.PreProcessing import Preprocessor
from Utility.CDPConfigValues import CDPConfigValues
from prediction.Constants import CoreFx, OpenCV, Springboot


class DailyTaskExecutor:
    """
        Core class used to trigger the functionality of prediction.
    """

    def __init__(self):
        pass

    @staticmethod
    def execute_prediction(project_id, raw_input_df):
        """ 
            Class method used to trigger the functionality for data prediction and LIME validation.
		
			:param project_id: Project ID whose data to be processed.
            :type project_id: str
            
			:param raw_input_df: Dataframe object, data to be processed for predection.
            :type: raw_input_df: DataFrame
            
            :return Dataframe obejct, that contains prediction and LIME analysis.
		
        """
        try:
            if constants.SPRINGBOOT_ID == project_id:
                project_obj = Springboot()
            elif constants.OPENCV_ID == project_id:
                project_obj = OpenCV()
            elif constants.COREFX_ID == project_id:
                project_obj = CoreFx()
            else:
                print("Wrong Project Id Provided...")
                return

            if project_obj is not None:
                raw_input_df.to_csv(project_obj.RAW_CDP_FILE_NAME, index=False)

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

                obj.predict()

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

                lr.lime_analysis()
                output_df = pd.read_csv(project_obj.OUTPUT_FILE, index_col=None)
                return output_df

        except Exception as e:
            print(e)

    def execute(self, project):
        """
            Method used to preprocess the data and dump the data analysis report.
		
            :param project:Project ID
            :type project_id: str
		
        """
        prediction = PrepareCommitsIssuesDataForPrediction(project)
        start_time = time.time()

        if os.path.exists(f"{prediction.current_day_directory}/{CDPConfigValues.final_feature_file}"):
            pre_processed_df = pd.read_csv(f"{prediction.current_day_directory}/{CDPConfigValues.final_feature_file}")
        else:
            prediction.get_commit_and_bug_data()
            prediction.pre_process_data()
            pre_processed_df = pd.read_csv(f"{prediction.current_day_directory}/{CDPConfigValues.final_feature_file}")

        include_merge_files = ast.literal_eval(CDPConfigValues.configFetcher.get("include_merge_files", project))
        project_name = CDPConfigValues.configFetcher.get('name', project)

        if include_merge_files:
            no_of_days_merge_files_to_include = int(
                CDPConfigValues.configFetcher.get("no_of_days_merge_files_to_include", project))

            pre_processed_df_without_merge = pre_processed_df[
                ~(pre_processed_df["COMMIT_MESSAGE"].str.contains("Merge", na=False))]
            pre_processed_df_with_merge = pre_processed_df[
                pre_processed_df["COMMIT_MESSAGE"].str.contains("Merge", na=False)]

            pre_processed_df_with_merge = pre_processed_df_with_merge.apply(
                lambda x: x.str.strip() if x.dtype == "object" else x)
            pre_processed_df_with_merge['COMMITTER_TIMESTAMP'] = pd.to_datetime(
                pre_processed_df_with_merge['COMMITTER_TIMESTAMP'])
            pre_processed_df_with_merge = pre_processed_df_with_merge.sort_values(by=["COMMITTER_TIMESTAMP"],
                                                                                  ascending=[False])
            latest_df_timestamp = pre_processed_df_with_merge["COMMITTER_TIMESTAMP"].to_list()[0]
            pre_processed_df_with_merge = pre_processed_df_with_merge.loc[
                pre_processed_df_with_merge["COMMITTER_TIMESTAMP"] >= (pd.Timestamp(latest_df_timestamp) -
                                                                       pd.to_timedelta(
                                                                           f"{no_of_days_merge_files_to_include}day"))]

            pre_processed_df = pd.concat([pre_processed_df_without_merge, pre_processed_df_with_merge],
                                         ignore_index=True)
            pre_processed_df.to_csv(f"{prediction.current_day_directory}/pre_processed_file_before_pre_process.csv",
                                    index=False)
            preprocessor = Preprocessor(project, pre_processed_df, preprocessed=True)
            preprocessor.drop_unnecessary_columns()
            preprocessor.get_no_of_files_count()
            preprocessor.rename()
            preprocessor.update_file_name_directory()
            preprocessor.get_no_of_directories_count()
            pre_processed_df = preprocessor.github_data_dump_df
        else:
            pre_processed_df = pre_processed_df[~pre_processed_df["COMMIT_MESSAGE"].str.contains("Merge", na=False)]
            preprocessor = Preprocessor(project, pre_processed_df, preprocessed=True)
            preprocessor.drop_unnecessary_columns()
            preprocessor.get_no_of_files_count()
            preprocessor.rename()
            preprocessor.update_file_name_directory()
            preprocessor.get_no_of_directories_count()
            pre_processed_df = preprocessor.github_data_dump_df
        insert_predicted_data_in_db = InsertPredictedDataInDB()
        raw_git_data = RawGitDataInDB(project)
        project_id = raw_git_data.get_project_id()
        pre_processed_df.to_csv(f"{prediction.current_day_directory}/pre_processed_file.csv", index=False)

        days = 0
        if pre_processed_df is not None and len(pre_processed_df) != 0:

            pre_processed_df['TIMESTAMP'] = pd.to_datetime(pre_processed_df['TIMESTAMP'])
            pre_processed_df = pre_processed_df.sort_values(by=["TIMESTAMP"], ascending=[False])
            latest_df_timestamp = str(pre_processed_df["TIMESTAMP"].to_list()[0])

            override_days = ast.literal_eval(CDPConfigValues.configFetcher.get("override_days", project))
            if override_days:
                days = int(CDPConfigValues.configFetcher.get("days", project))
            else:
                days = raw_git_data.get_number_of_days_to_fetch_data()

            date_after = (pd.Timestamp(latest_df_timestamp) - pd.to_timedelta(f"{days}day"))
            query_date = (datetime.today().utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            data_frame_for_db = pre_processed_df.loc[pre_processed_df['TIMESTAMP'] >= date_after]
            data_frame_for_db.drop_duplicates(keep=False, inplace=True)
            data_frame_for_db.to_csv(f"{prediction.current_day_directory}/data_frame_for_db.csv", index=False)
            prediction_df = insert_predicted_data_in_db.get_prediction_listing_data(project_id)
            if prediction_df is not None:
                data_frame_for_db = data_frame_for_db[~((data_frame_for_db.COMMIT_ID.isin(prediction_df.COMMIT_ID) &
                                                         data_frame_for_db.FILE_NAME.isin(prediction_df.FILE_NAME) &
                                                         data_frame_for_db.FILE_PARENT.isin(
                                                             prediction_df.FILE_PARENT)))]

            if data_frame_for_db is not None and len(data_frame_for_db) != 0:
                data_frame_for_db["TIMESTAMP"] = data_frame_for_db["TIMESTAMP"].astype(str)
                raw_git_data.insert_commit_details_to_db(data_frame_for_db, project_id)
                prediction_df_length = len(data_frame_for_db)
                counter = 0
                while counter < prediction_df_length:
                    data_frame_for_prediction = data_frame_for_db.iloc[counter:counter + 500]
                    predicted_df = self.execute_prediction(project_id, data_frame_for_prediction)
                    if predicted_df is not None:
                        predicted_df.to_csv(f"{prediction.current_day_directory}/predicted_data_{counter}.csv", index=False)
                        insert_predicted_data_in_db.insert_data_into_prediction_listing(project, project_id, predicted_df)
                        insert_predicted_data_in_db.insert_explainablecdp_data(project_id, predicted_df)
                        insert_predicted_data_in_db.calculate_feature_trend(project_id, query_date)
                        insert_predicted_data_in_db.update_prediction_summary(project_id, days)
                    else:
                        print("No data is predicted...")
                    counter = counter + 500
            else:
                print("No New data is available to insert into DB...")
        else:
            print("No New data Found to insert into Database...")

        insert_predicted_data_in_db.update_prediction_summary(project_id, days)
        query_date = (datetime.today().utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        insert_predicted_data_in_db.calculate_feature_trend(project_id, query_date)
        end_time = time.time()
 
        return 1


if __name__ == "__main__":
    dailyTaskExecutor = DailyTaskExecutor()
    #dailyTaskExecutor.execute("project_3") #coreFx
    dailyTaskExecutor.execute("project_2") #openCV
    dailyTaskExecutor.execute("project_1") #spring-boot
