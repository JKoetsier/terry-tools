#!/bin/bash


python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/accbiqh_no_indices/ --breakpoints=all:25,monetdb:5
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/accbiqh_sharecompanyserver/ --breakpoints=mssql:5,all:5
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/accbiqh_indices/ --breakpoints=all:15,mysql:4
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/tpch_no_indices --tpch=true
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/tpch_indices --tpch=true
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/tpch_indices_tweak_settings
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/tpch_indices_tweak_settings_desc_index
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/aws_tpch_mysql_sf1/indices --tpch=true
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/aws_tpch_mysql_sf1/indices_tweak_settings --breakpoints=all:1250,mysql:1250 --tpch=true
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/aws_tpch_mysql_sf1/indices_tweak_settings_desc_index --tpch=true
python graph/plotgraphs.py ~/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/aws_tpch_mysql_sf1/indices_tweak_settings_desc_index_settings2 --tpch=true

python graph/plotgraphs.py graph/mapping_mysql_accbiqh_before_after.txt --outputfile=/Users/jaapkoetsier/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/thesis_graphs/AccBiqhLocalMySQLNoIndicesIndices.png
python graph/plotgraphs.py graph/mapping_mysql_aws_tpch_indices_settings.txt --outputfile=/Users/jaapkoetsier/Desktop/MasterThesis/msc-thesis-experiments-data/experiments_results/thesis_graphs/TpchAwsSideBySide.png --tpch=true
