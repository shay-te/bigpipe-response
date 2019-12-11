import os


class TestUtils(object):

    @staticmethod
    def empty_output_folder(output_path):
        # empty output directory
        for root, dirs, files in os.walk(output_path):
            for file in files:
                print('Delete file :  {}'.format(file))
                os.remove(os.path.join(root, file))
