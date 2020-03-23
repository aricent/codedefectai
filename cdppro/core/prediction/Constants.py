SPRINGBOOT_ID = 1
OPENCV_ID = 2
COREFX_ID = 3


class Springboot:
    """
    Class containing config values for Spring-boot Project
    :param  MODEL_PICKLE_FILE_NAME: Pickle file name of the trained model
    :type  MODEL_PICKLE_FILE_NAME: str
    
    :param  PCA_PICKLE_FILE_NAME: Pickle file name of the PCA model, if applicable.
    :type  PCA_PICKLE_FILE_NAME: str
    
    :param  MIN_MAX_SCALER_PICKLE_FILE_NAME: Pickle file name of the MinMaxScaler model.
    :type  MIN_MAX_SCALER_PICKLE_FILE_NAME: str
    
    :param  IMPUTER_PICKLE_FILE_NAME: Pickle file name of the Imputer model.
    :type  IMPUTER_PICKLE_FILE_NAME: str
    
    :param  PCA_REQUIRED: Flag used, if PCA is required or not.
    :type  PCA_REQUIRED: Bool
    
    :param  ONE_HOT_ENCODING_REQUIRED: Flag used, if One Hot Encoding is required or not.
    :type  ONE_HOT_ENCODING_REQUIRED: Bool
    
    :param  COLUMNS_TO_BE_DROPPED: Columns-name to be dropped.
    :type  COLUMNS_TO_BE_DROPPED: list
    
    :param  COLUMNS_TO_BE_ONE_HOT_ENCODED: Columns-name to be one hot encoded.
    :type  COLUMNS_TO_BE_ONE_HOT_ENCODED: list
    
    :param  CATEGORICAL_COLUMNS: Columns-name of categorical type.
    :type  CATEGORICAL_COLUMNS:list
    
    :param  SCALED_INPUT_FILE_NAME: File name used to save normalised data.
    :type  SCALED_INPUT_FILE_NAME: str
    
    :param  FILE_TYPE_TO_BE_PROCESSED: Files extension to be analysed.
    :type  FILE_TYPE_TO_BE_PROCESSED: list
    
    :param  THRESHOLD: Threshold value for model prediction.
    :type  THRESHOLD: float
    
    :param  RAW_TRAINING_DATA_FILE_NAME: File name used to save raw training data.
    :type  RAW_TRAINING_DATA_FILE_NAME: str
    
    :param  SCALED_TRAINING_DATA_FILE_NAME: File name used to save scaled training data.
    :type  SCALED_TRAINING_DATA_FILE_NAME: str
    
    :param  RAW_CDP_FILE_NAME: File name used to save raw CDP data.
    :type  RAW_CDP_FILE_NAME: str
    
    :param  OUTPUT_FILE: File name used to save output data.
    :type  OUTPUT_FILE: str
    """
    FILE_TYPE_TO_BE_PROCESSED = '.java'
    COLUMNS_TO_BE_DROPPED = [
        'AUTHOR_NAME',
        'FILE_NAME',
        'FILE_STATUS',
        'FILE_PARENT',
        'COMMIT_ID',
        'TIMESTAMP',
        'CONTENTS_URL',
        'MONTH',
        'DATE',
        'HOUR',
        'SUNDAY',
        'MONDAY',
        'TUESDAY',
        'WEDNESDAY',
        'THURSDAY',
        'FRIDAY',
        'SATURDAY',
        'DEV_REXP_CALENDER_YEAR_WISE',
        'NS',
        'NF',
    ]

    COLUMNS_TO_BE_ONE_HOT_ENCODED = ['FILE_STATUS']
    CATEGORICAL_COLUMNS = ['COMMIT_TYPE', 'IsFix', 'FILE_ADDED', 'FILE_DELETED', 'FILE_MODIFIED', 'FILE_RENAMED']
    MODEL_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/model.pkl"
    PCA_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/pca.pkl"
    IMPUTER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/imputer.pkl"
    MIN_MAX_SCALER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/minMaxScaler.pkl"
    RAW_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/rawtrainingdata.csv"
    SCALED_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/scaledtrainingdata.csv"
    RAW_CDP_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/rawData.csv"
    SCALED_INPUT_FILE_NAME = "/cdpscheduler/prediction/Models/springboot/intermediate.csv"
    OUTPUT_FILE = "/cdpscheduler/prediction/Models/springboot/output.csv"
    ONE_HOT_ENCODING_REQUIRED = True
    PCA_REQUIRED = False
    THRESHOLD = 0.5


class OpenCV:
    """
    Class containing config values for OpenCV Project
    :param  MODEL_PICKLE_FILE_NAME: Pickle file name of the trained model
    :type  MODEL_PICKLE_FILE_NAME: str
    
    :param  PCA_PICKLE_FILE_NAME: Pickle file name of the PCA model, if applicable.
    :type  PCA_PICKLE_FILE_NAME: str
    
    :param  MIN_MAX_SCALER_PICKLE_FILE_NAME: Pickle file name of the MinMaxScaler model.
    :type  MIN_MAX_SCALER_PICKLE_FILE_NAME: str
    
    :param  IMPUTER_PICKLE_FILE_NAME: Pickle file name of the Imputer model.
    :type  IMPUTER_PICKLE_FILE_NAME: str
    
    :param  PCA_REQUIRED: Flag used, if PCA is required or not.
    :type  PCA_REQUIRED: Bool
    
    :param  ONE_HOT_ENCODING_REQUIRED: Flag used, if One Hot Encoding is required or not.
    :type  ONE_HOT_ENCODING_REQUIRED: Bool
    
    :param  COLUMNS_TO_BE_DROPPED: Columns-name to be dropped.
    :type  COLUMNS_TO_BE_DROPPED: list
    
    :param  COLUMNS_TO_BE_ONE_HOT_ENCODED: Columns-name to be one hot encoded.
    :type  COLUMNS_TO_BE_ONE_HOT_ENCODED: list
    
    :param  CATEGORICAL_COLUMNS: Columns-name of categorical type.
    :type  CATEGORICAL_COLUMNS:list
    
    :param  SCALED_INPUT_FILE_NAME: File name used to save normalised data.
    :type  SCALED_INPUT_FILE_NAME: str
    
    :param  FILE_TYPE_TO_BE_PROCESSED: Files extension to be analysed.
    :type  FILE_TYPE_TO_BE_PROCESSED: list
    
    :param  THRESHOLD: Threshold value for model prediction.
    :type  THRESHOLD: float
    
    :param  RAW_TRAINING_DATA_FILE_NAME: File name used to save raw training data.
    :type  RAW_TRAINING_DATA_FILE_NAME: str
    
    :param  SCALED_TRAINING_DATA_FILE_NAME: File name used to save scaled training data.
    :type  SCALED_TRAINING_DATA_FILE_NAME: str
    
    :param  RAW_CDP_FILE_NAME: File name used to save raw CDP data.
    :type  RAW_CDP_FILE_NAME: str
    
    :param  OUTPUT_FILE: File name used to save output data.
    :type  OUTPUT_FILE: str
    """
    FILE_TYPE_TO_BE_PROCESSED = ('.hpp', '.cpp', '.h', '.cc', '.h', '.c',
                                 '.py', '.java', '.cl')
    COLUMNS_TO_BE_DROPPED = [
        'AUTHOR_NAME',
        'FILE_NAME',
        'FILE_STATUS',
        'FILE_PARENT',
        'COMMIT_ID',
        'TIMESTAMP',
        'CONTENTS_URL',
        'MONTH',
        'DATE',
        'HOUR',
        'SUNDAY',
        'MONDAY',
        'TUESDAY',
        'WEDNESDAY',
        'THURSDAY',
        'FRIDAY',
        'SATURDAY',
        'DEV_REXP_CALENDER_YEAR_WISE',
        'NS',
        'ND'
    ]

    COLUMNS_TO_BE_ONE_HOT_ENCODED = ['FILE_STATUS']
    CATEGORICAL_COLUMNS = ['COMMIT_TYPE', 'IsFix', 'FILE_ADDED', 'FILE_DELETED', 'FILE_MODIFIED', 'FILE_RENAMED']
    MODEL_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/model.pkl"
    PCA_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/pca.pkl"
    IMPUTER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/imputer.pkl"
    MIN_MAX_SCALER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/minMaxScaler.pkl"
    RAW_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/rawtrainingdata.csv"
    SCALED_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/scaledtrainingdata.csv"
    RAW_CDP_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/rawData.csv"
    SCALED_INPUT_FILE_NAME = "/cdpscheduler/prediction/Models/opencv/intermediate.csv"
    OUTPUT_FILE = "/cdpscheduler/prediction/Models/opencv/output.csv"
    ONE_HOT_ENCODING_REQUIRED = True
    PCA_REQUIRED = False
    THRESHOLD = 0.5


class CoreFx:
    """
    Class containing config values for CoreFx Project
    :param  MODEL_PICKLE_FILE_NAME: Pickle file name of the trained model
    :type  MODEL_PICKLE_FILE_NAME: str
    
    :param  PCA_PICKLE_FILE_NAME: Pickle file name of the PCA model, if applicable.
    :type  PCA_PICKLE_FILE_NAME: str
    
    :param  MIN_MAX_SCALER_PICKLE_FILE_NAME: Pickle file name of the MinMaxScaler model.
    :type  MIN_MAX_SCALER_PICKLE_FILE_NAME: str
    
    :param  IMPUTER_PICKLE_FILE_NAME: Pickle file name of the Imputer model.
    :type  IMPUTER_PICKLE_FILE_NAME: str
    
    :param  PCA_REQUIRED: Flag used, if PCA is required or not.
    :type  PCA_REQUIRED: Bool
    
    :param  ONE_HOT_ENCODING_REQUIRED: Flag used, if One Hot Encoding is required or not.
    :type  ONE_HOT_ENCODING_REQUIRED: Bool
    
    :param  COLUMNS_TO_BE_DROPPED: Columns-name to be dropped.
    :type  COLUMNS_TO_BE_DROPPED: list
    
    :param  COLUMNS_TO_BE_ONE_HOT_ENCODED: Columns-name to be one hot encoded.
    :type  COLUMNS_TO_BE_ONE_HOT_ENCODED: list
    
    :param  CATEGORICAL_COLUMNS: Columns-name of categorical type.
    :type  CATEGORICAL_COLUMNS:list
    
    :param  SCALED_INPUT_FILE_NAME: File name used to save normalised data.
    :type  SCALED_INPUT_FILE_NAME: str
    
    :param  FILE_TYPE_TO_BE_PROCESSED: Files extension to be analysed.
    :type  FILE_TYPE_TO_BE_PROCESSED: list
    
    :param  THRESHOLD: Threshold value for model prediction.
    :type  THRESHOLD: float
    
    :param  RAW_TRAINING_DATA_FILE_NAME: File name used to save raw training data.
    :type  RAW_TRAINING_DATA_FILE_NAME: str
    
    :param  SCALED_TRAINING_DATA_FILE_NAME: File name used to save scaled training data.
    :type  SCALED_TRAINING_DATA_FILE_NAME: str
    
    :param  RAW_CDP_FILE_NAME: File name used to save raw CDP data.
    :type  RAW_CDP_FILE_NAME: str
    
    :param  OUTPUT_FILE: File name used to save output data.
    :type  OUTPUT_FILE: str
    
    """
    FILE_TYPE_TO_BE_PROCESSED = ('.cs', '.h', '.c', '.vb')
    COLUMNS_TO_BE_DROPPED = [
        'AUTHOR_NAME',
        'FILE_NAME',
        'FILE_STATUS',
        'FILE_PARENT',
        'COMMIT_ID',
        'TIMESTAMP',
        'CONTENTS_URL',
        'MONTH',
        'DATE',
        'HOUR',
        'SUNDAY',
        'MONDAY',
        'TUESDAY',
        'WEDNESDAY',
        'THURSDAY',
        'FRIDAY',
        'SATURDAY',
        'DEV_REXP_CALENDER_YEAR_WISE',
        'NS',
        'ND'
        ]

    #CATEGORICAL_COLUMNS = ['IsFix']
    #COLUMNS_TO_BE_ONE_HOT_ENCODED = []
    COLUMNS_TO_BE_ONE_HOT_ENCODED = ['FILE_STATUS']
    CATEGORICAL_COLUMNS = ['COMMIT_TYPE', 'IsFix', 'FILE_ADDED', 'FILE_DELETED', 'FILE_MODIFIED', 'FILE_RENAMED']
    MODEL_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/model.pkl"
    PCA_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/pca.pkl"
    IMPUTER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/imputer.pkl"
    MIN_MAX_SCALER_PICKLE_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/minMaxScaler.pkl"
    RAW_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/rawtrainingdata.csv"
    SCALED_TRAINING_DATA_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/scaledtrainingdata.csv"
    RAW_CDP_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/rawData.csv"
    SCALED_INPUT_FILE_NAME = "/cdpscheduler/prediction/Models/corefx/intermediate.csv"
    OUTPUT_FILE = "/cdpscheduler/prediction/Models/corefx/output.csv"
    ONE_HOT_ENCODING_REQUIRED = True
    PCA_REQUIRED = False
    THRESHOLD = 0.5
