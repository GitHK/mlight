from tests.common import drop_all_collections


def setup_package():
    drop_all_collections()
    print('Test suite setup complete')


def teardown_package():
    drop_all_collections()
    print('Test suite teardown complete.')
