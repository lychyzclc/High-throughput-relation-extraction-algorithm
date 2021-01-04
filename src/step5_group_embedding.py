import argparse
import logging
import os
import pickle

from tqdm import tqdm

from util.load_embedding import LoadCuiEmbedding
from util.load_entity_pair import LoadEntitypairs
from util.logger import get_logger

logger = logging.getLogger(__name__)


class EmbeddingMatch:
    def __init__(self, load_path, save_path, embed_path):
        self.load_path = load_path
        self.save_path = save_path
        self.embed_path = embed_path

    def init(self):
        entitypair_loader = LoadEntitypairs(self.load_path)
        logger.info('- loading entitypairs...')
        entitypair_loader.loader()
        self.grouped_pairs = entitypair_loader.dic
        logger.info('- done')
        self.embed_loader = LoadCuiEmbedding(self.embed_path)
        logger.info('- loading cui embeddings...')
        if not os.path.exists(self.embed_path):
            logger.info('building...')
            self.embed_loader.build()
        self.embed_loader.load()
        logger.info('- done')

    def process(self, label, sample_type):
        with open(self.save_path, 'w') as f:
            for cui1, rel, cui2 in tqdm(self.grouped_pairs):
                embed1 = self.embed_loader.get_embed(cui1)
                embed2 = self.embed_loader.get_embed(cui2)
                f.writelines('|'.join([
                    cui1, cui2,
                    str(self.grouped_pairs[(cui1, rel, cui2)]), embed1, embed2,
                    str(label[(cui1, cui2)]),
                    str(sample_type)
                ]) + '\n')


def generate_positive_sample(load_path, save_path, embed_path, label,
                             sample_type):
    generator = EmbeddingMatch(load_path, save_path, embed_path)
    generator.init()
    generator.process(label, sample_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file',
                        action='store',
                        type=str,
                        help='The path to input sentences')
    parser.add_argument('--output_file',
                        action='store',
                        type=str,
                        help='The path to output sentences')
    parser.add_argument('--embed_file',
                        action='store',
                        type=str,
                        help='The path to load embedding')
    parser.add_argument('--log_file',
                        action='store',
                        type=str,
                        help='The path to save logs')
    parser.add_argument('--label',
                        action='store',
                        type=str,
                        help='relation mapping file')
    parser.add_argument(
        '--sample_type',
        action='store',
        type=int,
        default=0,
        help='0 for positive, num greater than 0 indicates negative sample type'
    )

    args = parser.parse_args()

    logger = get_logger(logger, args.log_file)

    with open(args.label, "rb") as f:
        label_mapping = pickle.load(f)
    generate_positive_sample(args.input_file, args.output_file,
                             args.embed_file, label_mapping, args.sample_type)
