# HISTOGRAM KEYS
AST_EDGE_HISTOGRAM_KEY = 'edge_histogram'
TOKEN_HISTOGRAM_KEY = 'token_histogram'
TOKEN_HISTOGRAM_NO_KEYWORDS_KEY = 'token_histogram_no_keywords'
TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY = 'token_histogram_no_keywords_and_numbers'

JAVA_KEYWORDS = ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'continue',
                 'const', 'default', 'do', 'double', 'else', 'enum', 'exports', 'extends', 'final', 'finally', 'float',
                 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'module',
                 'native', 'new', 'package', 'private', 'protected', 'public', 'requires', 'return', 'short', 'static',
                 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'var',
                 'void', 'volatile', 'while']

# PATHS
HISTORICAL_ENTROPY_ROOT = 'commit-entropy-historical'
PROJECT_SNAPSHOT_ROOT = 'project-snapshot'
GLOBAL_CONTEXT_ROOT = 'global-context'

# METRICS KEYS
AST_EDGE_FILE_KEY = 'entropy_ast_edge_file_context'
AST_EDGE_FILE_NORMALISED_KEY = 'entropy_ast_edge_file_normalised'
AST_EDGE_PROJECT_KEY = 'entropy_ast_edges_project_context'
AST_EDGE_PROJECT_NORMALISED_KEY = 'entropy_ast_edge_project_normalised'

TOKEN_FILE_KEY = 'entropy_token_file_context'
TOKEN_FILE_NORMALISED_KEY = 'entropy_token_file_normalised'
TOKEN_PROJECT_KEY = 'entropy_token_project_context'
TOKEN_PROJECT_NORMALISED_KEY = 'entropy_token_project_normalised'

TOKEN_NO_KEYWORDS_FILE_KEY = 'entropy_token_no_keywords_file_context'
TOKEN_NO_KEYWORDS_FILE_NORMALISED_KEY = 'entropy_token_no_keywords_file_normalised'
TOKEN_NO_KEYWORDS_PROJECT_KEY = 'entropy_token_no_keywords_project_context'
TOKEN_NO_KEYWORDS_PROJECT_NORMALISED_KEY = 'entropy_token_no_keywords_project_normalised'

TOKEN_NO_KEYWORDS_NO_NUMBERS_FILE_KEY = 'entropy_token_no_keywords_no_numbers_file_context'
TOKEN_NO_KEYWORDS_NO_NUMBER_FILE_NORMALISED_KEY = 'entropy_token_no_keywords_no_numbers_file_normalised'
TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_KEY = 'entropy_token_no_keywords_no_numbers_project_context'
TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_NORMALISED_KEY = 'entropy_token_no_keywords_no_numbers_project_normalised'

EXPERIMENT_PROJECTS_LIST = ['apollo', 'arduino', 'dagger', 'deeplearning4j', 'fresco', 'ghidra', 'grpc-java', 'graal', 'guice', 'hikaricp', 'jedis',
                'jib', 'libgdx', 'lombok', 'material-components-android', 'mockito', 'mybatis-3','netty', 'realm-java', 'skywalking' ,'redisson', 'thingsboard', 'vert.x', 'zipkin', 'zxing']
