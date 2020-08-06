#!/bin/bash

. settings.ini

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
        then
        # Argument is null
        return 0
    else
        # Grep DB name in the list of databases
        sudo -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}


function write_log() {
    echo $1
    echo "" &>> log/install_db.log
    echo "" &>> log/install_db.log
    echo "--------------------" &>> log/install_db.log
    echo $1 &>> log/install_db.log
    echo "--------------------" &>> log/install_db.log
}

if database_exists $db_name
then
        if $drop_apps_db
            then
            echo "Drop database..."
            sudo -u postgres -s dropdb $db_name
        else
            echo "Database exists but the settings file indicates that we don't have to drop it."
            exit
        fi
fi



write_log "Create extension"
sudo -u postgres -s createdb -O $user_pg $db_name 
sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgis;" &> log/install_db.log
sudo -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";' &>> log/install_db.log



write_log 'Create users schema'
wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub.sql -P /tmp
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub.sql  &>> log/install_db.log

write_log 'Add some example data into users'
wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-data.sql -P /tmp
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub-data.sql  &>> log/install_db.log
wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-dataset.sql -P /tmp
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub-dataset.sql &>> log/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/users_hub_geoconstats.sql &>> log/install_db.log
write_log 'Create ref_geo'
wget https://raw.githubusercontent.com/PnX-SI/GeoNature/$ref_geo_release/data/core/ref_geo.sql -P /tmp
sudo sed -i "s/MYLOCALSRID/$srid_local/g" /tmp/ref_geo.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/ref_geo.sql &>> log/install_db.log

if [ ! -f '/tmp/communes_fr_admin_express_2020-02.zip' ]
then
    wget  --cache=off http://geonature.fr/data/ign/communes_fr_admin_express_2020-02.zip -P /tmp
else
    echo "/tmp/communes_fr_admin_express_2020-02.zip already exist"
fi
unzip /tmp/communes_fr_admin_express_2020-02.zip -d /tmp

write_log 'Add municipalities secteurs coeur aa to ref geo'

sudo -n -u postgres -s psql -d $db_name -f /tmp/fr_municipalities.sql &>> log/install_db.log
sudo -n -u postgres -s psql -d $db_name -c "ALTER TABLE ref_geo.temp_fr_municipalities OWNER TO $user_pg;" &>> log/install_db.log
wget https://raw.githubusercontent.com/PnX-SI/GeoNature/$ref_geo_release/data/core/ref_geo_municipalities.sql -P /tmp
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/ref_geo_municipalities.sql &>> log/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/l_areas_secteur_aa_coeur.sql &>> log/install_db.log

write_log 'Create database structure'
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/scriptSQL_Constats.sql &>> log/install_db.log

write_log 'Add some example data into constats_loups schema'
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/sample_data.sql &>> log/install_db.log

rm /tmp/*.sql
rm /tmp/*.zip