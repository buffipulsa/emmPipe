
import os
from ngSkinTools2 import api as ngst_api

class NgSkinData():

    def exportNgSkinData(self, node, path):

        if not os.path.exists('{}/ngSkinData'.format(path)):
            os.makedirs('{}/ngSkinData'.format(path))

        outFileName = os.path.join(path, 'ngSkinData', '{}.json'.format(node))
        ngst_api.export_json(node, file=outFileName)

    def importNgSkinData(self, node, path):

        # configure how influences described in a file will be matched against the scene
        config = ngst_api.InfluenceMappingConfig()
        config.use_distance_matching = True
        config.use_name_matching = False
        config.globs = [('L_*', 'R_*'), ('*_l_*', '*_r_*')]

        # run the import
        ngst_api.import_json(node,
                             file=os.path.join(path, '{}.json'.format(node)),
                             vertex_transfer_mode=ngst_api.VertexTransferMode.vertexId,
                             influences_mapping_config=config)