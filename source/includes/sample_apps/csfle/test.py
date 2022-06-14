import unittest
from pymongo import MongoClient
from bson.binary import Binary
from const import (
    BUILD_DIR,
    DIR_SEPERATOR,
    NODE,
    NODE_FLE_2,
    GO,
    CSHARP,
    PYTHON,
    PYTHON_FLE_2,
    JAVA,
    AWS_TEST,
    AZURE_TEST,
    GCP_TEST,
    LOCAL_TEST,
    FILE_MAP,
    DEK,
    INSERT,
)
import os
import ntpath

DB_NAME = "medicalRecords"
COLLECTION_NAME = "patients"
KEY_VAULT_DB = "encryption"
KEY_VAULT_COLL = "__keyVault"
CURRENT_DIRECTORY = os.getcwd()
NUM_QE_DEKS = 4
BSON_BINARY_VALUE = Binary(b"")
TEST_FLE1_ENC_FIELD = "bloodType"
TEST_FLE2_ENC_FIELD = "patientId"


class TestTutorials(unittest.TestCase):

    client = MongoClient(os.getenv("MONGODB_URI"))

    def _dropData(self):
        self.client[DB_NAME][COLLECTION_NAME].drop()
        self.client[KEY_VAULT_DB][KEY_VAULT_COLL].drop()

    def startTestRun(self):
        self._dropData()

    def setUp(self):
        os.chdir(CURRENT_DIRECTORY)
        self._dropData()

    def tearDown(self):
        self._dropData()

    def _check_docs(self, language):
        """Checks that expected documents were added to key vault and collection and that fields were encrypted"""

        if language in [NODE_FLE_2, PYTHON_FLE_2]:
            self.assertEqual(
                self.client[KEY_VAULT_DB][KEY_VAULT_COLL].count_documents({}),
                NUM_QE_DEKS,
            )
            self.assertEqual(
                self.client[DB_NAME][COLLECTION_NAME].count_documents(
                    {"firstName": "Jon"}
                ),
                1,
            )
            self.assertEqual(
                type(
                    self.client[DB_NAME][COLLECTION_NAME].find_one(
                        {"firstName": "Jon"}
                    )[TEST_FLE2_ENC_FIELD]
                ),
                type(BSON_BINARY_VALUE),
                f"{TEST_FLE2_ENC_FIELD} must be encrypted",
            )
        else:
            self.assertEqual(
                self.client[KEY_VAULT_DB][KEY_VAULT_COLL].count_documents({}), 1
            )
            self.assertEqual(
                self.client[DB_NAME][COLLECTION_NAME].count_documents(
                    {"name": "Jon Doe"}
                ),
                1,
            )
            self.assertEqual(
                type(
                    self.client[DB_NAME][COLLECTION_NAME].find_one({"name": "Jon Doe"})[
                        TEST_FLE1_ENC_FIELD
                    ]
                ),
                type(BSON_BINARY_VALUE),
                f"{TEST_FLE1_ENC_FIELD} must be encrypted",
            )

    def _check_app(self, language):
        """Build and test a sample application"""

        make_dek_file_name = None
        insert_file_name = None
        commands = []
        if language == PYTHON or language == PYTHON_FLE_2:
            make_dek_file_name = FILE_MAP[language][DEK]
            insert_file_name = FILE_MAP[language][INSERT]
            commands.append(f"python {make_dek_file_name}")
            commands.append(f"python {insert_file_name}")
        elif language == JAVA:
            make_dek_file_name = os.path.splitext(
                ntpath.basename(FILE_MAP[language][DEK])
            )[0]
            insert_file_name = os.path.splitext(
                ntpath.basename(FILE_MAP[language][INSERT])
            )[0]
            commands.append(
                f'mvn compile exec:java -Dexec.mainClass="com.mongodb.csfle.{make_dek_file_name}"'
            )
            commands.append(
                f'mvn compile exec:java -Dexec.mainClass="com.mongodb.csfle.{insert_file_name}"'
            )
        elif language == CSHARP:
            os.chdir("CSFLE")
            commands.append("dotnet run")
        elif language == NODE or language == NODE_FLE_2:
            make_dek_file_name = FILE_MAP[language][DEK]
            insert_file_name = FILE_MAP[language][INSERT]
            commands.append("npm install")
            commands.append(f"node {make_dek_file_name}")
            commands.append(f"node {insert_file_name}")
        elif language == GO:
            make_dek_file_name = FILE_MAP[language][DEK]
            insert_file_name = FILE_MAP[language][INSERT]
            commands.append("go get .")
            commands.append(f"go fmt {make_dek_file_name}")
            commands.append(f"go fmt {insert_file_name}")
            commands.append("go run -tags=cse .")
        else:
            Exception("Failed to Handle Language")
        for c in commands:
            print(c)
            os.system(c)
        self._check_docs(language)


class TestPython(TestTutorials):
    """Test Python FLE1 Sample Apps"""

    def test_python_aws(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON)

    def test_python_azure(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON)

    def test_python_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON)

    def test_python_local(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON)


class TestPythonFLE2(TestTutorials):
    """Test Python FLE2 Sample Apps"""

    def test_python_fle_2_aws(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON_FLE_2, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON_FLE_2)

    def test_python_fle_2_azure(self):
        os.chdir(
            os.path.join(BUILD_DIR, PYTHON_FLE_2, *AZURE_TEST.split(DIR_SEPERATOR))
        )
        self._check_app(PYTHON_FLE_2)

    def test_python_fle_2_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, PYTHON_FLE_2, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(PYTHON_FLE_2)

    def test_python_fle_2_local(self):
        os.chdir(
            os.path.join(BUILD_DIR, PYTHON_FLE_2, *LOCAL_TEST.split(DIR_SEPERATOR))
        )
        self._check_app(PYTHON_FLE_2)


class TestDotnet(TestTutorials):
    """Test Dotnet FLE1 Sample Apps"""

    def test_dotnet_aws(self):
        os.chdir(os.path.join(BUILD_DIR, CSHARP, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(CSHARP)

    def test_dotnet_azure(self):
        os.chdir(os.path.join(BUILD_DIR, CSHARP, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(CSHARP)

    def test_dotnet_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, CSHARP, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(CSHARP)

    def test_dotnet_local(self):
        os.chdir(os.path.join(BUILD_DIR, CSHARP, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(CSHARP)


class TestNode(TestTutorials):
    """Test Node FLE1 Sample Apps"""

    def test_node_aws(self):
        os.chdir(os.path.join(BUILD_DIR, NODE, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE)

    def test_node_azure(self):
        os.chdir(os.path.join(BUILD_DIR, NODE, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE)

    def test_node_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, NODE, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE)

    def test_node_local(self):
        os.chdir(os.path.join(BUILD_DIR, NODE, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE)


class TestNodeFLE2(TestTutorials):
    """Test Node FLE2 Sample Apps"""

    def test_node_fle_2_aws(self):
        os.chdir(os.path.join(BUILD_DIR, NODE_FLE_2, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE_FLE_2)

    def test_node_fle_2_azure(self):
        os.chdir(os.path.join(BUILD_DIR, NODE_FLE_2, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE_FLE_2)

    def test_node_fle_2_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, NODE_FLE_2, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE_FLE_2)

    def test_node_fle_2local(self):
        os.chdir(os.path.join(BUILD_DIR, NODE_FLE_2, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(NODE_FLE_2)


class TestGo(TestTutorials):
    """Test Go FLE1 Sample Apps"""

    def test_go_aws(self):
        os.chdir(os.path.join(BUILD_DIR, GO, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(GO)

    def test_go_azure(self):
        os.chdir(os.path.join(BUILD_DIR, GO, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(GO)

    def test_go_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, GO, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(GO)

    def test_go_local(self):
        os.chdir(os.path.join(BUILD_DIR, GO, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(GO)


class TestJava(TestTutorials):
    """Test Java FLE1 Sample Apps"""

    def test_java_aws(self):
        os.chdir(os.path.join(BUILD_DIR, JAVA, *AWS_TEST.split(DIR_SEPERATOR)))
        self._check_app(JAVA)

    def test_java_azure(self):
        os.chdir(os.path.join(BUILD_DIR, JAVA, *AZURE_TEST.split(DIR_SEPERATOR)))
        self._check_app(JAVA)

    def test_java_gcp(self):
        os.chdir(os.path.join(BUILD_DIR, JAVA, *GCP_TEST.split(DIR_SEPERATOR)))
        self._check_app(JAVA)

    def test_java_local(self):
        os.chdir(os.path.join(BUILD_DIR, JAVA, *LOCAL_TEST.split(DIR_SEPERATOR)))
        self._check_app(JAVA)
