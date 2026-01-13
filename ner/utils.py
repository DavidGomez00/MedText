import os
import pandas as pd


def cantemist2df(ann_path):
    ''' Parsea anotaciones de Cantemist para hacer un dataframe estructurado.
    
        Input: Un fichero de anotación de cantemist. 
        Output: Un dataframe con la anotación estructurada.
    '''
    # Comprueba que el fichero no esté vacío
    if os.path.getsize(ann_path) == 0:
        return pd.DataFrame(columns=['term_idx', 'text', 'category', 'char_start', 'char_end', 'ICD-O Code'])
    
    # Lee el fichero de anotación
    ann = pd.read_csv(
        ann_path,
        sep = '\t',
        dtype=str,
        encoding='utf-8',
        header=None
    )

    # Parsea la parte de las coordenadas
    nota_coords = ann[ann[0].str.startswith('T')].copy()
    split = nota_coords[1].str.split(' ', expand=True)
    nota_coords = pd.concat([nota_coords[[0, 2]], split], axis=1)
    nota_coords.columns = ['term_idx', 'text', 'category', 'char_start', 'char_end']

    # Parsea las filas de anotación
    nota_ann = ann[ann[0].str.startswith('#')].copy()
    nota_ann[0] = nota_ann[0].str.replace('#', 'T')
    nota_ann = nota_ann.drop(1, axis=1)
    nota_ann.columns = ['term_idx', 'ICD-O Code']

    # Merge de las dos partes
    merged = pd.merge(nota_coords, nota_ann, on='term_idx', how='inner')

    return merged
