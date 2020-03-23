import traceback
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine

from DataBaseAccess.MariaDB import MariaDB
from Utility.CDPConfigValues import CDPConfigValues


class InsertPredictedDataInDB:
    """
        Class used to extract and place prediction data into DB
        """
	
    def __init__(self):
        self.maria_db = ""
        self.engine = ""

    def insert_data_into_prediction_listing(self, project, project_id, processed_dataframe):
        """
            Method used to insert prediction data in to DB file.
			
            :param project: Name of the project.
			:type project: str
            
            :param project_id: Project ID.
            :type project_id: str
            
			:paramprocessed_dataframe: Dataframe object which contain pediction and LIME analysis.
			:type paramprocessed_dataframe: DataFrame
        """
		
		
        data_frame_for_db = processed_dataframe[["COMMIT_ID", "TIMESTAMP", "FILE_NAME", "FILE_PARENT", "FILE_STATUS", "Prediction", "Confidence"]].copy()
        data_frame_for_db.columns = ["COMMIT_ID", "TIMESTAMP", "FILE_NAME", "FILE_PARENT", "FILE_STATUS", "Prediction", "ConfidenceScore"]

        try:
            data_frame_for_db["Project_Id"] = project_id
            print("Creating SQLAlchemy Connection...")
            self.engine = create_engine(f"mysql+pymysql://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}?ssl_ca=/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem",
                                        echo=True)

            # While Executing in the local comment the above sql connecion and uncommnet the bellow one
            # self.engine = create_engine(
            #     f'mysql+mysqldb://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}')

            data_frame_for_db.to_sql(name='predictionlisting', con=self.engine, if_exists='append', index=False)
            self.engine.dispose()

        except Exception as e:
            print(e)
            print(f"Exception Occurred!!!\n{traceback.print_exc()}")
            traceback.print_stack()
            print("Closing sqlalchemy connection for maria_db")
            self.engine.dispose()

    def update_prediction_summary(self, project_id, days):
        """
            Method used to update prediction data for a specific time period.
		
			:param project_id: Project ID whose data to be updated.
            :type project_id: str
            
			:param days: Timeperiod for which the data to be updated.
            :type days: int
        """

        self.maria_db = MariaDB(host=CDPConfigValues.host, port=CDPConfigValues.port, database=CDPConfigValues.database,
                                user_name=CDPConfigValues.username, password=CDPConfigValues.password)

        summary_date = (datetime.today().utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            query = f"select count(distinct(COMMIT_ID)), count(FILE_NAME) from predictionlisting " \
                f"where Project_Id={project_id} and timestamp>='{summary_date}';"

            cursor = self.maria_db.execute_query(query)
            result_set = cursor.fetchall()
            total_commits_for_prediction = result_set[0][0]
            total_files_for_prediction = result_set[0][1]

            query = f"select count(FILE_NAME) from predictionlisting where Project_Id={project_id} and Prediction=1 " \
                f"and timestamp>='{summary_date}'; "
            cursor = self.maria_db.execute_query(query)
            result_set = cursor.fetchall()
            buggy_predictions = result_set[0][0]

            query = f"update projectsummary set TotalFilesForPrediction = {total_files_for_prediction}, " \
                f"TotalCommitsForPrediction = {total_commits_for_prediction}, BuggyPredictions = {buggy_predictions} " \
                f"where projectid = {project_id};"

            self.maria_db.execute_query(query)

            self.maria_db.close_connection()

        except Exception as e:
            print("Exception occurred...closing maria_db database connections")
            print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
            traceback.print_stack()
            print({e.__traceback__})
            self.maria_db.close_connection()

    def get_prediction_listing_data(self, project_id):
        """
            Method used to extract the prediction data from the DB
		
			:param project_id: Project ID whose data to be fetch.
            :type project_id: str
		
			:return Dataframe object which contains the fetched results.
        """
        self.maria_db = MariaDB(host=CDPConfigValues.host, port=CDPConfigValues.port, database=CDPConfigValues.database,
                                user_name=CDPConfigValues.username, password=CDPConfigValues.password)

        query = f"Select PredictionListingId, COMMIT_ID, FILE_NAME, FILE_PARENT, FILE_STATUS, TimeStamp " \
            f"From predictionlisting Where Project_Id = {project_id}"

        cursor = self.maria_db.execute_query(query)
        raw_data = cursor.fetchall()
        self.maria_db.close_connection()
        result = []
        for row in raw_data:
            result.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        result_df = pd.DataFrame(result, columns=["PredictionListingId", "COMMIT_ID", "FILE_NAME", "FILE_PARENT",
                                                  "FILE_STATUS", "TIMESTAMP"])
        return result_df

    @staticmethod
    def form_ecdp_data(row, project_id):

        result_list = []

        if "LIME_LINES_DELETED" in row.index:
            result_list.append((row["PredictionListingId"], "Lines Deleted", "LINES_DELETED", row["LINES_DELETED"],
                                0 if row["LIME_LINES_DELETED"] < 0 else 1, abs(round(row["LIME_LINES_DELETED"], 4)),
                                "Number", project_id))

        if "LIME_ND" in row.index:
            result_list.append((row["PredictionListingId"], "Directories Modified For Commit", "ND", row["ND"],
                                0 if row["LIME_ND"] < 0 else 1, abs(round(row["LIME_ND"], 4)), "Number", project_id))

        if "LIME_IsFix" in row.index:
            result_list.append((row["PredictionListingId"], "Whether Issues Fixed", "Is_fix", row["IsFix"],
                                0 if row["LIME_IsFix"] < 0 else 1, abs(round(row["LIME_IsFix"], 4)),
                                "Boolean", project_id))

        if "LIME_FILES_ENTROPY" in row.index:
            result_list.append((row["PredictionListingId"], "Change Entropy", "FILES_ENTROPY", row["FILES_ENTROPY"],
                                0 if row["LIME_FILES_ENTROPY"] < 0 else 1, abs(round(row["LIME_FILES_ENTROPY"], 4)),
                                "Number", project_id))

        if "LIME_FileChanges" in row.index:
            result_list.append((row["PredictionListingId"], "File Changes", "FileChanges", row["FileChanges"],
                                0 if row["LIME_FileChanges"] < 0 else 1, abs(round(row["LIME_FileChanges"], 4)),
                                "Number", project_id))

        if "LIME_COMMIT_TYPE" in row.index:
            result_list.append((row["PredictionListingId"], "Commit Type", "COMMIT_TYPE", row["COMMIT_TYPE"],
                                0 if row["LIME_FileChanges"] < 0 else 1, abs(round(row["LIME_COMMIT_TYPE"], 4)),
                                "Number", project_id))

        if "LIME_FILE_AGE" in row.index:
            result_list.append((row["PredictionListingId"], "File Age", "FILE_AGE", int(row["FILE_AGE"] / (3600 * 24)),
                                0 if row["LIME_FILE_AGE"] < 0 else 1, abs(round(row["LIME_FILE_AGE"], 4)),
                                "Day(s)", project_id))

        if "LIME_NO_OF_DEV" in row.index:
            result_list.append((row["PredictionListingId"], "Developers Count", "NO_OF_DEV", row["NO_OF_DEV"],
                                0 if row["LIME_NO_OF_DEV"] < 0 else 1, abs(round(row["LIME_NO_OF_DEV"], 4)),
                                "Number", project_id))

        if "LIME_TIMES_FILE_MODIFIED" in row.index:
            result_list.append((row["PredictionListingId"], "Times File Modified", "TIMES_FILE_MODIFIED",
                                row["TIMES_FILE_MODIFIED"],0 if row["LIME_TIMES_FILE_MODIFIED"] < 0 else 1,
                                abs(round(row["LIME_TIMES_FILE_MODIFIED"], 4)), "Number", project_id))

        if "LIME_FILE_SIZE" in row.index:
            result_list.append((row["PredictionListingId"], "File Size", "FILE_SIZE",
                                round(float(row["FILE_SIZE"] / 1024), 2), 0 if row["LIME_FILE_SIZE"] < 0 else 1,
                                abs(round(row["LIME_FILE_SIZE"], 4)), "KB", project_id))

        if "LIME_NF" in row.index:
            result_list.append((row["PredictionListingId"], "Files Modified For Commit", "NF", row["NF"],
                                0 if row["LIME_NF"] < 0 else 1, abs(round(row["LIME_NF"], 4)), "Number", project_id))

        if "LIME_NS" in row.index:
            result_list.append((row["PredictionListingId"], "Submodules Modified", "NS", row["NS"],
                                0 if row["LIME_NS"] < 0 else 1, abs(round(row["LIME_NS"], 4)), "Number", project_id))

        if "LIME_DEV_REXP_365_DAYS_WISE" in row.index:
            result_list.append((row["PredictionListingId"], "Recent Developer Experience", "DEV_REXP",
                               row["DEV_REXP_365_DAYS_WISE"],0 if row["LIME_DEV_REXP_365_DAYS_WISE"] < 0 else 1,
                               abs(round(row["LIME_DEV_REXP_365_DAYS_WISE"], 4)), "Number", project_id))

        if "LIME_DEV_STATS" in row.index:
            result_list.append((row["PredictionListingId"], "Developer Experience", "DEV_EXP", row["DEV_STATS"],
                                0 if row["LIME_DEV_STATS"] < 0 else 1, abs(round(row["LIME_DEV_STATS"], 4)), "Number",
                                project_id))

        if "LIME_SUB_MODULE_STATS" in row.index:
            result_list.append((row["PredictionListingId"], "Developer Module Experience", "SUB_MODULE_STATS",
                                row["SUB_MODULE_STATS"],0 if row["LIME_SUB_MODULE_STATS"] < 0 else 1,
                                abs(round(row["LIME_SUB_MODULE_STATS"], 4)), "Number", project_id))

        result_df = pd.DataFrame(result_list,
                                 columns=["PredictionListingId", "FeatureName", "FeatureKey", "FeatureValue",
                                          "FeatureLabel", "FeatureCoefficient", "FeatureUnits", "ProjectId"])

        return result_df

    def insert_explainablecdp_data(self, project_id, data_frame):
        """
            Method used to insert LIME data to DB.
			
            :param project_id: Project ID whose data to be insreted.
            :type project_id: str
            
			:param data_frame:	Dataframe object contains the data to be inserted.		
		    :type data_frame: DataFrame
        """
        db_frame = self.get_prediction_listing_data(project_id)
        db_frame = db_frame.sort_values(by=["TIMESTAMP"], ascending=[True])
        data_frame = data_frame.sort_values(by=["TIMESTAMP"], ascending=[True])
        timestamp = data_frame["TIMESTAMP"].to_list()[0]
        db_frame = db_frame.loc[db_frame["TIMESTAMP"] >= timestamp]

        merged_df = pd.merge(data_frame, db_frame, how="right",
                             left_on=["COMMIT_ID", "FILE_NAME", "FILE_PARENT", "FILE_STATUS"],
                             right_on=["COMMIT_ID", "FILE_NAME", "FILE_PARENT", "FILE_STATUS"])

        merged_df = merged_df.dropna(axis=0)
        result_df = pd.DataFrame()
        for index, row in merged_df.iterrows():
            result_df = pd.concat([result_df, self.form_ecdp_data(row, project_id)], ignore_index=True)

        result_df["ProjectId"] = result_df["ProjectId"].astype(int)

        try:
            print("Creating SQLAlchemy Connection...")
            self.engine = create_engine(
                f"mysql+pymysql://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}?ssl_ca=/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem",
                echo=True)
            # While Executing in the local comment the above sql connecion and uncommnet the bellow one
            # self.engine = create_engine(
            #     f'mysql+mysqldb://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}')
            result_df.to_sql(name='explainablecdp', con=self.engine, if_exists='append', index=False)

            self.engine.dispose()
        except Exception as e:
            print("Exception occurred...closing sqlalchemy connection for maria db")
            print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
            traceback.print_stack()
            print({e.__traceback__})
            self.engine.dispose()

    @staticmethod
    def trend_analysis(data, project_id):
        """
            Method used to extract the trend, used to render Box-Plot.
		
			:param project_id: Project ID whose data to be rendered.
			:type project_id: str
		"""

        trend_df = pd.DataFrame(data)
        trend_df["prediction"] = trend_df["prediction"].astype(int)
        trend_df["featurecoefficient"] = trend_df["featurecoefficient"].astype(float)
        result = []

        feature_label = [0, 1]
        for feature in feature_label:
            trend_df_clean = trend_df.loc[trend_df["prediction"] == feature].copy()
            if len(trend_df_clean) != 0:
                trend_df_clean['actual_coefficient'] = trend_df_clean[["featurecoefficient", "featurelabel"]].apply(
                    lambda r: r["featurecoefficient"] * -1 if r["featurelabel"] == 0 else r["featurecoefficient"],
                    axis=1
                )

                feature_list = []
                list_keys = list(set(trend_df_clean["featurekey"].to_list()))
                for key in list_keys:
                    feature_list.append(
                        (trend_df_clean.loc[trend_df_clean["featurekey"] == key]["featurename"].to_list()[0], key,
                         trend_df_clean.loc[trend_df_clean["featurekey"] == key]["actual_coefficient"].median()))

                feature_data_frame = pd.DataFrame(feature_list, columns=["featurename", "featurekey", "median"])

                feature_data_frame = feature_data_frame.sort_values("median", ascending=False)
                feature_data_frame = feature_data_frame.reset_index()

                for index in feature_data_frame.index:
                    row = feature_data_frame.loc[index]

                    result.append([
                        str(row["featurename"]),
                        round(float(row["median"]), 4),
                        round(trend_df_clean.loc[trend_df_clean["featurekey"] == row["featurekey"]]
                              ["actual_coefficient"].quantile([.25]).to_list()[0], 4),
                        round(trend_df_clean.loc[trend_df_clean["featurekey"] == row["featurekey"]]
                              ["actual_coefficient"].quantile([.75]).to_list()[0], 4),
                        round(float(trend_df_clean.loc[trend_df_clean["featurekey"] == row["featurekey"]]
                                    ["actual_coefficient"].max()), 4),
                        round(float(trend_df_clean.loc[trend_df_clean["featurekey"] == row["featurekey"]]
                                    ["actual_coefficient"].min()), 4),
                        feature,
                        project_id
                    ])
                    
        feature_result = pd.DataFrame(result,
                                      columns=["FeatureName", "median", "firstQuartile", "thirdQuartile",
                                               "minimum", "maximum", "Prediction", "ProjectId"])

        return feature_result

    def calculate_feature_trend(self, project_id, feature_date):

        query = f"select pl.Prediction, ecdp.featurename, ecdp.FeatureKey, ecdp.FeatureLabel, ecdp.FeatureCoefficient " \
            f"from explainablecdp ecdp, predictionlisting pl " \
            f"where ecdp.PredictionListingId = pl.PredictionListingId and ecdp.ProjectId = {project_id} " \
            f"and pl.TimeStamp>='{feature_date}'"

        try:
            self.maria_db = MariaDB(host=CDPConfigValues.host, port=CDPConfigValues.port,
                                    database=CDPConfigValues.database,
                                    user_name=CDPConfigValues.username, password=CDPConfigValues.password)

            cursor = self.maria_db.execute_query(query)
            raw_data = cursor.fetchall()
            feature_trend_df = pd.DataFrame(raw_data)
            feature_trend_df.columns = ["prediction", "featurename", "featurekey", "featurelabel", "featurecoefficient"]
            feature_trend_df = self.trend_analysis(feature_trend_df, project_id)
            feature_trend_df["Prediction"] = feature_trend_df["Prediction"].astype(int)
            """changes for fixing predctionfeaturetrend issue"""
            feature_label = [0, 1]
            for feature in feature_label:
                feature_trend_df_predicted = feature_trend_df.loc[feature_trend_df["Prediction"] == feature].copy()
                query = f"select count(*) from predctionfeaturetrend where projectid={project_id} and prediction = {feature}"
                cursor = self.maria_db.execute_query(query)
                raw_data = cursor.fetchall()
                if raw_data is not None:
                    raw_data = raw_data[0][0]
                
                print("Creating SQLAlchemy Connection...")
                self.engine = create_engine(
                f"mysql+pymysql://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}?ssl_ca=/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem",
                echo=True)
                if raw_data is not None and raw_data == 0:
                    feature_trend_df_predicted.to_sql(name='predctionfeaturetrend', con=self.engine, if_exists='append', index=False)
                else:
                    queries = ""
                    for index, row in feature_trend_df_predicted.iterrows():
                        query = f"Update predctionfeaturetrend Set median={row['median']}, " \
                            f"firstQuartile={row['firstQuartile']}, thirdQuartile={row['thirdQuartile']}, " \
                            f"minimum={row['minimum']}, maximum={row['maximum']} where projectId={row['ProjectId']} and " \
                            f"prediction={row['Prediction']} and featurename='{row['FeatureName']}';\n"

                        with self.engine.connect() as connection:
                            with self.engine.begin():
                                connection.execute(query)
                        print(f"Query -- {query}")

                self.engine.dispose()
            self.maria_db.close_connection()
            """changes end"""
            
#            query = f"select count(*) from predctionfeaturetrend where projectid={project_id}"
#            cursor = self.maria_db.execute_query(query)
#            raw_data = cursor.fetchall()
#            if raw_data is not None:
#                raw_data = raw_data[0][0]
#            self.maria_db.close_connection()
#
#            print("Creating SQLAlchemy Connection...")
#            self.engine = create_engine(
#                f"mysql+pymysql://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}?ssl_ca=/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem",
#                echo=True)
#
#            # While Executing in the local comment the above sql connecion and uncommnet the bellow one
#            # self.engine = create_engine(
#            #     f'mysql+mysqldb://{CDPConfigValues.username}:{CDPConfigValues.password}@{CDPConfigValues.host}:{CDPConfigValues.port}/{CDPConfigValues.database}')
#
#            if raw_data is not None and raw_data == 0:
#                feature_trend_df.to_sql(name='predctionfeaturetrend', con=self.engine, if_exists='append', index=False)
#            else:
#                queries = ""
#                for index, row in feature_trend_df.iterrows():
#                    """if in any case prediction is not 1 when table is populated for the first time, It will never update table as there will be 
#                    no record where prediction would be 1"""
#                    query = f"Update predctionfeaturetrend Set median={row['median']}, " \
#                        f"firstQuartile={row['firstQuartile']}, thirdQuartile={row['thirdQuartile']}, " \
#                        f"minimum={row['minimum']}, maximum={row['maximum']} where projectId={row['ProjectId']} and " \
#                        f"prediction={row['Prediction']} and featurename='{row['FeatureName']}';\n"
#
#                    with self.engine.connect() as connection:
#                        with self.engine.begin():
#                            connection.execute(query)
#                    print(f"Query -- {query}")
#
#            self.engine.dispose()

        except Exception as e:
            print("Exception occurred...closing maria_db database connections")
            print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
            traceback.print_stack()
            if self.maria_db.conn.is_connected():
                self.maria_db.close_connection()
            self.engine.dispose()
            raise e


if __name__ == "__main__":
    insertPredictedDataInDB = InsertPredictedDataInDB()
    query_date = (datetime.today().utcnow() - timedelta(days=15)).strftime("%Y-%m-%d")
    insertPredictedDataInDB.calculate_feature_trend(2, query_date)
