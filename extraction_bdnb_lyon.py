# Parameters
departement = '69' #ex. 1 pour l'Ain, 69 pour le Rhône, 974 pour la Réunion
commune_nom = "Lyon-Villeurbanne"
codes_postaux = ['69001','69002','69003','69004','69005','69006','69007','69008','69009','69100']
communes_codes = [69381,69382,69383,69384,69385,69386,69387,69388,69389,69266]
dbname = "bdnb_69_2025"
tablename = "bdnb_2025_07_a_open_data_dep69" #Must be changed manually for now in each cursor.execute() request...

# Libs
import func
import os
import requests
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import tqdm
import psycopg2
import shapely as shp

#Set directories
working_dir = os.getcwd()
data_dir = f"{working_dir}/data{departement}"
output_dir = f"{working_dir}/outputs{departement}"
if os.path.exists(output_dir):
    pass
else:
    os.mkdir(output_dir)

#Runs

ModuleExtractTable_proprietaire = True
ModuleExtractTable_rel_batiment_groupe_proprietaire = True
ModuleExtractTable_batiment_groupe = True
ModuleExtractTable_batiment_groupe_dpe_representatif_logement = True
ModuleExtractTable_batiment_groupe_dpe_statistique_logement = True
ModuleExtractTable_batiment_groupe_ffo_bat = True
ModuleExtractTable_rel_batiment_groupe_adresse = True
ModuleExtractTable_adresse = True
ModuleMergeData = True
ModuleGroupStatistics = True


#ModuleExtractTable_batiment_groupe

if ModuleExtractTable_batiment_groupe is True:

    print("ModuleExtractTable_batiment_groupe")

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for cc in tqdm.tqdm([str(x) for x in communes_codes]):
                #Get values
                cur.execute(
                            """SELECT 
                            batiment_groupe_id, 
                            geom_groupe 
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.batiment_groupe
                            WHERE 
                            code_commune_insee = %s""",
                            (cc,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv",index=False)

else:
    pass



#ModuleExtractTable_rel_batiment_groupe_proprietaire

if ModuleExtractTable_rel_batiment_groupe_proprietaire is True:

    print("ModuleExtractTable_rel_batiment_groupe_proprietaire")

    #Get the list of personne_ids (personne_id = concat(num_departement,num_majic) > len = 8)
    bat = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv")
    bat_groupe_ids = list(set(bat['batiment_groupe_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for bgi in tqdm.tqdm(bat_groupe_ids):
                #Get values
                cur.execute(
                            """SELECT
                            personne_id,
                            batiment_groupe_id,
                            nb_locaux_open
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.rel_batiment_groupe_proprietaire 
                            WHERE 
                            batiment_groupe_id = %s""",
                            (bgi,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    

    #Merge with FichierDesLocaux ON personne_id
    #merged_df = df.merge(natprop, on='personne_id', how='inner')

    #Save
    df.to_csv(f"{output_dir}/rel_batiment_groupe_proprietaire_{commune_nom}.csv",index=False)

    print(df.head())
    
else:
    pass




#ModuleExtractTable_proprietaire

if ModuleExtractTable_proprietaire is True:

    print("ModuleExtractTable_proprietaire")

    #Get the list of personne_ids (personne_id = concat(num_departement,num_majic) > len = 8)
    bat = pd.read_csv(f"{output_dir}/rel_batiment_groupe_proprietaire_{commune_nom}.csv")
    personnes_ids = list(set(bat['personne_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for pid in tqdm.tqdm(personnes_ids):
                #Get values
                cur.execute(
                            """SELECT
                            personne_id,
                            siren,
                            forme_juridique,
                            denomination,
                            code_postal,
                            libelle_commune,
                            nb_locaux_open
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.proprietaire 
                            WHERE 
                            personne_id = %s""",
                            (pid,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    

    #Merge with FichierDesLocaux ON personne_id
    #merged_df = df.merge(natprop, on='personne_id', how='inner')

    #Save
    df.to_csv(f"{output_dir}/proprietaire_{commune_nom}.csv",index=False)

    print(df.head())
    print(df.shape)
    
else:
    pass




#ModuleExtractTable_batiment_groupe_dpe_representatif_logement

if ModuleExtractTable_batiment_groupe_dpe_representatif_logement is True:

    print("ModuleExtractTable_batiment_groupe_dpe_representatif_logement")

    #Get bat_groupe_id list
    bat = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv")
    bat_groupe_ids = list(set(bat['batiment_groupe_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for bgi in tqdm.tqdm(bat_groupe_ids):
                #Get values
                cur.execute(
                            """SELECT
                            batiment_groupe_id,
                            classe_bilan_dpe,
                            type_installation_chauffage,
                            type_isolation_mur_exterieur,
                            materiaux_structure_mur_exterieur,
                            type_dpe,
                            type_batiment_dpe
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.batiment_groupe_dpe_representatif_logement 
                            WHERE 
                            batiment_groupe_id = %s""",
                            (bgi,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/batiment_groupe_dpe_representatif_logement_{commune_nom}.csv",index=False)

else:
    pass


#ModuleExtractTable_batiment_groupe_dpe_statistique_logement

if ModuleExtractTable_batiment_groupe_dpe_statistique_logement is True:

    print("ModuleExtractTable_batiment_groupe_dpe_statistique_logement")

    #Get bat_groupe_id list
    bat = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv")
    bat_groupe_ids = list(set(bat['batiment_groupe_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for bgi in tqdm.tqdm(bat_groupe_ids):
                #Get values
                cur.execute(
                            """SELECT
                            batiment_groupe_id,
                            nb_classe_bilan_dpe_a,
                            nb_classe_bilan_dpe_b,
                            nb_classe_bilan_dpe_c,
                            nb_classe_bilan_dpe_d,
                            nb_classe_bilan_dpe_e,
                            nb_classe_bilan_dpe_f,
                            nb_classe_bilan_dpe_g
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.batiment_groupe_dpe_statistique_logement 
                            WHERE 
                            batiment_groupe_id = %s""",
                            (bgi,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/batiment_groupe_dpe_statistique_logement_{commune_nom}.csv",index=False)

else:
    pass


#ModuleExtractTable_batiment_groupe_ffo_bat

if ModuleExtractTable_batiment_groupe_ffo_bat is True:

    print("ModuleExtractTable_batiment_groupe_ffo_bat")

    #Get bat_groupe_id list
    bat = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv")
    bat_groupe_ids = list(set(bat['batiment_groupe_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for bgi in tqdm.tqdm(bat_groupe_ids):
                #Get values
                cur.execute(
                            """SELECT
                            batiment_groupe_id,
                            nb_log,
                            usage_niveau_1_txt,
                            annee_construction
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.batiment_groupe_ffo_bat 
                            WHERE 
                            batiment_groupe_id = %s""",
                            (bgi,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/batiment_groupe_ffo_bat_{commune_nom}.csv",index=False)

else:
    pass


#ModuleExtractTable_rel_batiment_groupe_adresse

if ModuleExtractTable_rel_batiment_groupe_adresse is True:

    print("ModuleExtractTable_rel_batiment_groupe_adresse")

    #Get bat_groupe_id list
    bat = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv")
    bat_groupe_ids = list(set(bat['batiment_groupe_id']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for bgi in tqdm.tqdm(bat_groupe_ids):
                #Get values
                cur.execute(
                            """SELECT
                            batiment_groupe_id,
                            cle_interop_adr
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.rel_batiment_groupe_adresse 
                            WHERE 
                            batiment_groupe_id = %s""",
                            (bgi,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/rel_batiment_groupe_adresse_{commune_nom}.csv",index=False)

else:
    pass


#ModuleExtractTable_adresse

if ModuleExtractTable_adresse is True:

    print("ModuleExtractTable_adresse")

    #Get bat_groupe_id list
    adr = pd.read_csv(f"{output_dir}/rel_batiment_groupe_adresse_{commune_nom}.csv")
    adresses = list(set(adr['cle_interop_adr']))

    #Extract from SQL dump of bdnb

    results = []
    
    with psycopg2.connect(f"dbname={dbname} user=postgres") as conn:

        with conn.cursor() as cur:

            for a in tqdm.tqdm(adresses):
                #Get values
                cur.execute(
                            """SELECT
                            cle_interop_adr,
                            numero,
                            rep,
                            nom_voie,
                            type_voie,
                            code_postal,
                            libelle_commune
                            FROM 
                            bdnb_2025_07_a_open_data_dep69.adresse 
                            WHERE 
                            cle_interop_adr = %s""",
                            (a,))
                # Get column names
                # Get column names from first query only
                if not results and cur.description:
                    colnames = [desc[0] for desc in cur.description]

                rows = cur.fetchall()
                results.extend(rows)

    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=colnames)
    print(df.head())

    #Save
    df.to_csv(f"{output_dir}/adresse_{commune_nom}.csv",index=False)

else:
    pass


#Merge data 

if ModuleMergeData is True:

    print("ModuleMergeData")

    df0 = pd.read_csv(f"{output_dir}/proprietaire_{commune_nom}.csv") #personne_id, fichierFoncier
    df1 = pd.read_csv(f"{output_dir}/rel_batiment_groupe_proprietaire_{commune_nom}.csv") #batiment_groupe_id, personne_id
    df2 = pd.read_csv(f"{output_dir}/batiment_groupe_{commune_nom}.csv") #batiment_groupe_id, geom
    df3 = pd.read_csv(f"{output_dir}/batiment_groupe_dpe_representatif_logement_{commune_nom}.csv") #batiment_groupe_id, bdnb_dpe
    df4 = pd.read_csv(f"{output_dir}/batiment_groupe_ffo_bat_{commune_nom}.csv") #batiment_groupe_id, bdnb_ffo
    df5 = pd.read_csv(f"{output_dir}/batiment_groupe_dpe_statistique_logement_{commune_nom}.csv") #batiment_groupe_id, ademe_dpe
    dfA = pd.read_csv(f"{output_dir}/rel_batiment_groupe_adresse_{commune_nom}.csv") #batiment_groupe_id, cle_interop_adr
    dfB = pd.read_csv(f"{output_dir}/adresse_{commune_nom}.csv") #cle_interop_adr, adresse

    #batiment_goupe_id, cle_interop_adr, adresse
    dfA['cle_interop_adr'] = dfA['cle_interop_adr'].astype('string')
    dfB['cle_interop_adr'] = dfB['cle_interop_adr'].astype('string')
    mergedA = pd.merge(dfA, dfB, on='cle_interop_adr', how='left')
    print(mergedA.dtypes)
    #batiment_groupe_id, personne_id, prop
    df0['personne_id'] = df0['personne_id'].astype('string')
    df1['personne_id'] = df1['personne_id'].astype('string')
    merged0 = pd.merge(df1, df0, on='personne_id', how='left', suffixes=('_dans_batiment','_dans_MAJIC'))
    print(merged0.dtypes)
    #batiment_groupe_id, personne_id, prop, geom
    df2['batiment_groupe_id'] = df2['batiment_groupe_id'].astype('string')
    merged1 = pd.merge(df2, merged0, on='batiment_groupe_id', how='left')
    print(merged1.dtypes)
    #batiment_groupe_id, personne_id, prop, geom, bdnb_dpe
    df3['batiment_groupe_id'] = df3['batiment_groupe_id'].astype('string')
    merged2 = pd.merge(merged1, df3, on='batiment_groupe_id', how='left')
    print(merged2.dtypes)
    #batiment_groupe_id, personne_id, prop, geom, bdnb_dpe, bdnb_ffo
    df4['batiment_groupe_id'] = df4['batiment_groupe_id'].astype('string')
    merged3 = pd.merge(merged2, df4, on='batiment_groupe_id', how='left')
    print(merged3.dtypes)
    #batiment_groupe_id, personne_id, prop, geom, bdnb_dpe, bdnb_ffo, ademe_dpe
    df5['batiment_groupe_id'] = df5['batiment_groupe_id'].astype('string')
    merged4 = pd.merge(merged3, df5, on='batiment_groupe_id', how='left')
    print(merged4.dtypes)
    #batiment_groupe_id, personne_id, prop, geom, bdnb_dpe, bdnb_ffo, ademe_dpe, adresse
    mergedA['batiment_groupe_id'] = mergedA['batiment_groupe_id'].astype('string')
    merged5 = pd.merge(merged4, mergedA, on='batiment_groupe_id', how='left', suffixes=("_proprietaire", "_batiment"))
    print(merged5.dtypes)

    #Last filter on 'code_postal_batiment' to remove buildings not belonging to communes_codes...
    merged5.dropna(axis=0,subset=['code_postal_batiment'],inplace=True)
    merged5['code_postal_batiment'] = merged5['code_postal_batiment'].astype('int32')
    merged5_clean = merged5.loc[merged5['code_postal_batiment'].isin(int(x) for x in codes_postaux)]

    #Export to csv
    merged5_clean.to_csv(f"{output_dir}/natprop2bdnb_{commune_nom}.csv",index=False)
    
    #Export to gpkg
    merged5_clean['geometry'] = merged5_clean['geom_groupe'].apply(lambda x: shp.wkb.loads(bytes.fromhex(x)))
    gdf = gpd.GeoDataFrame(merged5_clean, geometry='geometry', crs="EPSG:2154")
    gdf.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}.gpkg", driver="GPKG")

    #Export to geojson with EPSG:4326 and without duplicates in 'batiment_groupe_id'
    gdf = gpd.read_file(f"{output_dir}/natprop2bdnb_{commune_nom}.gpkg", layer=f"natprop2bdnb_{commune_nom}")
    gdf_noduplicates = gdf.drop_duplicates(subset='batiment_groupe_id')
    gdf_geomonly = gdf_noduplicates[['batiment_groupe_id','geometry']]
    gdf_noduplicates.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}_EPSG2154_NoDuplicates.gpkg", driver="GPKG")
    gdf_geomonly.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}_EPSG2154_NoDuplicates_GeomOnly.gpkg", driver="GPKG")
    gdf.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}_EPSG2154.geojson", driver="GeoJSON")
    gdf = gdf.to_crs(epsg=4326)
    gdf.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}_EPSG4326.geojson", driver="GeoJSON")

else:
    pass

#ModuleGroupStatistics

if ModuleGroupStatistics is True: 

    print("ModuleGroupStatistics")

    gdf = gpd.read_file(f"{output_dir}/natprop2bdnb_{commune_nom}.gpkg")

    grouped_dict = {'batiment_groupe_id':[],
                    'nb_log':[],
                    'dpe':[],
                    'pourcentage_dpe_a':[],
                    'pourcentage_dpe_b':[],
                    'pourcentage_dpe_c':[],
                    'pourcentage_dpe_d':[],
                    'pourcentage_dpe_e':[],
                    'pourcentage_dpe_f':[],
                    'pourcentage_dpe_g':[],
                    'pourcentage_dpe_inconnu':[],
                    'cp':[],
                    'formes_juridiques':[],
                    'concentration_prop_max':[],
                    'concentration_prop_max_denomination':[],
                    #'proprietaires_dans_bat':[],
                    'adr':[],
                    'geometry':[]
    }

    for bgi in tqdm.tqdm(list(set(gdf['batiment_groupe_id']))):
    
        gdc = gdf.loc[gdf['batiment_groupe_id'].astype('string') == str(bgi)]
        gdc.reset_index(drop=True,inplace=True)
        
        grouped_dict['batiment_groupe_id'].append(str(bgi))
        if not pd.isna(gdc.loc[0,'nb_log']):
            grouped_dict['nb_log'].append(int(gdc.loc[0,'nb_log']))
        else:
            grouped_dict['nb_log'].append("")
        adresse = ""
        if not pd.isna(gdc.loc[0,'numero']):
            adresse = adresse + f"{int(gdc.loc[0,'numero'])} "
        if not pd.isna(gdc.loc[0,'rep']):
            adresse = adresse + f"{gdc.loc[0,'rep']} "
        if not pd.isna(gdc.loc[0,'type_voie']):
            adresse = adresse + f"{gdc.loc[0,'type_voie']} "
        if not pd.isna(gdc.loc[0,'nom_voie']):
            adresse = adresse + f"{gdc.loc[0,'nom_voie']} "
        if not pd.isna(gdc.loc[0,'code_postal_batiment']):
            adresse = adresse + f"{int(gdc.loc[0,'code_postal_batiment'])}"
        grouped_dict['adr'].append(adresse)
        if not pd.isna(gdc.loc[0,'classe_bilan_dpe']):
            grouped_dict['dpe'].append(gdc.loc[0,'classe_bilan_dpe'])
        else:
            grouped_dict['dpe'].append("")
        count = 0
        for letter in ['a','b','c','d','e','f','g']:
            if not pd.isna(gdc.loc[0,f'nb_classe_bilan_dpe_{letter}']) and not pd.isna(gdc.loc[0,'nb_log']) and not (gdc.loc[0,'nb_log']==0):
                score = np.round((int(gdc.loc[0,f'nb_classe_bilan_dpe_{letter}'])/int(gdc.loc[0,'nb_log']))*100,2)
                count += int(gdc.loc[0,f'nb_classe_bilan_dpe_{letter}'])
                grouped_dict[f'pourcentage_dpe_{letter}'].append(score)
            else:
                grouped_dict[f'pourcentage_dpe_{letter}'].append('NC')
        if not pd.isna(gdc.loc[0,'nb_log']) and int(gdc.loc[0,'nb_log']) >= 1:
            logSansDPE = np.round((int(gdc.loc[0,'nb_log'])-count)/int(gdc.loc[0,'nb_log'])*100,2)
            grouped_dict['pourcentage_dpe_inconnu'].append(logSansDPE)
        else:
            grouped_dict['pourcentage_dpe_inconnu'].append('NC')
        if not pd.isna(gdc.loc[0,'code_postal_batiment']):
            grouped_dict['cp'].append(int(gdc.loc[0,'code_postal_batiment']))
        else:
            grouped_dict['cp'].append("")
        formJur_list = []
        for formJur in list(set(gdc['forme_juridique'])):
            if not pd.isna(formJur):
                formJur_list.append(str(formJur))
            else:
                formJur_list.append("personne_physique")
        grouped_dict['formes_juridiques'].append(formJur_list)
        grouped_dict['geometry'].append(gdc.loc[0,'geometry'])
        #denom = list(set(gdc['denomination']))
        #grouped_dict['proprietaires_dans_bat'].append(denom)
        personnes_ids = list(set(gdc['personne_id']))
        if len(personnes_ids) >= 1:
            if not pd.isna(gdc['nb_locaux_open_dans_batiment']).any():
                grouped_dict['concentration_prop_max_denomination'].append(gdc.loc[gdc['nb_locaux_open_dans_batiment'].idxmax(), 'denomination'])
            else:
                grouped_dict['concentration_prop_max_denomination'].append('NC')
            concentration_prop = []
            if not pd.isna(gdc.loc[0,'nb_log']) and gdc.loc[0,'nb_log'] >= 1:
                for pid in personnes_ids:
                    tmp = gdc.loc[gdc['personne_id'].astype('string') == str(pid)]
                    tmp.reset_index(drop=True,inplace=True)
                    if not tmp.empty:
                        conc = int(tmp.loc[0,'nb_locaux_open_dans_batiment'])/int(gdc['nb_locaux_open_dans_batiment'].sum())
                        concentration_prop.append(conc)
                    else:
                        pass
                if len(concentration_prop) >= 1:
                    grouped_dict['concentration_prop_max'].append(max(concentration_prop))
                else:
                    grouped_dict['concentration_prop_max'].append("NC")
            else:
                grouped_dict['concentration_prop_max'].append("NC")
        else:
            grouped_dict['concentration_prop_max'].append("NC")

    
    grouped_gdf = gpd.GeoDataFrame(grouped_dict, geometry='geometry', crs="EPSG:2154")
    grouped_gdf.to_file(f"{output_dir}/natprop2bdnb_{commune_nom}_grouped.gpkg", driver='GPKG')

else:
    pass