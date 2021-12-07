sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgres_fdw;"

sudo -u postgres -s psql -d $db_name -c "CREATE SERVER geonaturedbserver FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host '$db_source_host', dbname '$db_source_name', port '$db_source_port');"
sudo -u postgres -s psql -d $db_name -c "ALTER SERVER geonaturedbserver OWNER TO $user_pg;" 
sudo -u postgres -s psql -d $db_name -c "CREATE USER MAPPING FOR $user_pg SERVER geonaturedbserver OPTIONS (user '$db_source_user', password '$db_source_pass') ;"

psql -h $db_host -d $db_name -U $user_pg -c "
IMPORT FOREIGN SCHEMA ref_geo
LIMIT TO (ref_geo.l_areas, ref_geo.bib_areas_types)
FROM SERVER geonaturedbserver INTO ref_geo ;

IMPORT FOREIGN SCHEMA utilisateurs
FROM SERVER geonaturedbserver INTO utilisateurs;
"