----------------CHAMPS A RENOMMER / AJOUTER---------------------

alter table constats_loups.t_constats rename column nb_victimes_mortes to nb_victimes_mort;
alter table constats_loups.t_constats rename column nb_victimes_blessees to nb_victimes_blesse;
alter table constats_loups.t_constats rename column nb_jours_agent to nb_jour_agent;
alter table constats_loups.t_constats add column id_secteur integer;
alter table constats_loups.t_constats add column id_commune integer;
alter table constats_loups.t_constats add column departement character varying(2);
alter table constats_loups.t_constats add column id_role integer;
alter table constats_loups.t_constats add column dans_coeur boolean;
alter table constats_loups.t_constats add column dans_aa boolean;

alter table constats_loups.t_constats_declaratifs rename column id_constat_declaratif to id_constat_d;
alter table constats_loups.t_constats_declaratifs rename column date_constat to date_constat_d;
alter table constats_loups.t_constats_declaratifs rename column date_attaque to date_attaque_d;
alter table constats_loups.t_constats_declaratifs rename column proprietaire to proprietaire_d;
alter table constats_loups.t_constats_declaratifs rename column type_animaux to type_animaux_d;
alter table constats_loups.t_constats_declaratifs rename column nb_victimes_mortes to nb_victimes_mort_d;
alter table constats_loups.t_constats_declaratifs rename column nb_victimes_blessees to nb_victimes_blesse_d;
alter table constats_loups.t_constats_declaratifs rename column statut to statut_d;

alter table constats_loups.t_constats_declaratifs add column id_secteur_d integer;
alter table constats_loups.t_constats_declaratifs add column id_commune_d integer;
alter table constats_loups.t_constats_declaratifs add column departement_d character varying(2);
alter table constats_loups.t_constats_declaratifs add column id_role integer;
alter table constats_loups.t_constats_declaratifs add column dans_coeur_d boolean;
alter table constats_loups.t_constats_declaratifs add column dans_aa_d boolean;
alter table constats_loups.t_constats_declaratifs add column geom geometry(Point,2154);

---------------CLE ETRANGERES--------------------------------------
alter table constats_loups.t_constats add constraint animaux_fkey FOREIGN KEY (type_animaux) REFERENCES constats_loups.bib_type_animaux (id);
alter table constats_loups.t_constats add CONSTRAINT commune_fkey FOREIGN KEY (id_commune) REFERENCES ref_geo.l_areas (id_area);
alter table constats_loups.t_constats add CONSTRAINT role_fkey FOREIGN KEY (id_role) REFERENCES utilisateurs.t_roles (id_role);
alter table constats_loups.t_constats add CONSTRAINT secteur_fkey FOREIGN KEY (id_secteur) REFERENCES ref_geo.l_areas (id_area);
alter table constats_loups.t_constats add CONSTRAINT statut_fkey FOREIGN KEY (statut) REFERENCES constats_loups.bib_statut (id);

alter table constats_loups.t_constats_declaratifs add constraint animaux_d_fkey FOREIGN KEY (type_animaux_d) REFERENCES constats_loups.bib_type_animaux (id);
alter table constats_loups.t_constats_declaratifs add CONSTRAINT commune_d_fkey FOREIGN KEY (id_commune_d) REFERENCES ref_geo.l_areas (id_area);
alter table constats_loups.t_constats_declaratifs add CONSTRAINT role_d_fkey FOREIGN KEY (id_role) REFERENCES utilisateurs.t_roles (id_role);
alter table constats_loups.t_constats_declaratifs add CONSTRAINT secteur_d_fkey FOREIGN KEY (id_secteur_d) REFERENCES ref_geo.l_areas (id_area);
alter table constats_loups.t_constats_declaratifs add CONSTRAINT statut_d_fkey FOREIGN KEY (statut_d) REFERENCES constats_loups.bib_statut (id);

----------------GENERATION CENTROID GEOM DEPUIS POLYGON POUR DECLA-------------------------------------------
update constats_loups.t_constats_declaratifs.geom as (SELECT ST_Centroid(constats_loups.t_constats_declaratifs.the_geom_polygon) FROM constats_loups.t_constats_declaratifs);
alter table constats_loups.t_constats_declaratifs drop column the_geom_polygon;

----------------LANCEMENT UPDATE DES TRIGGERS------------------------
UPDATE constats_loups.t_constats SET id_secteur=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=30 and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
UPDATE constats_loups.t_constats SET id_commune=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=25 and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
UPDATE constats_loups.t_constats SET departement=substring(ref_geo.l_areas.area_code from 1 for 2) from ref_geo.l_areas where id_commune=ref_geo.l_areas.id_area;
UPDATE constats_loups.t_constats SET dans_coeur=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=1;
UPDATE constats_loups.t_constats SET dans_aa=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=20;

UPDATE constats_loups.t_constats_declaratifs SET id_secteur_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=30 and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
UPDATE constats_loups.t_constats_declaratifs SET id_commune_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=25 and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
UPDATE constats_loups.t_constats_declaratifs SET departement_d=substring(ref_geo.l_areas.area_code from 1 for 2) from ref_geo.l_areas where id_commune_d=ref_geo.l_areas.id_area;
UPDATE constats_loups.t_constats_declaratifs SET dans_coeur_d=ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=1;
UPDATE constats_loups.t_constats_declaratifs SET dans_aa_d=ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=20;

-----------------FONCTIONS / TRIGGERS-----------------------------------------

CREATE OR REPLACE FUNCTION constats_loups.update_com_sec()
  RETURNS trigger AS
$BODY$
 DECLARE
 geom_change boolean; 
BEGIN
 geom_change = false;
 IF(TG_OP ='UPDATE') THEN
     SELECT INTO geom_change NOT ST_EQUALS(OLD.the_geom_point, NEW.the_geom_point);
 END IF;
 IF(TG_OP='INSERT' OR (TG_OP='UPDATE' AND geom_change)) THEN
    UPDATE constats_loups.t_constats SET id_secteur=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=30 and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats SET id_commune=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=25 and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats SET departement=substring(ref_geo.l_areas.area_code from 1 for 2) from ref_geo.l_areas where id_commune=ref_geo.l_areas.id_area;
    UPDATE constats_loups.t_constats SET dans_coeur=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=1;
    UPDATE constats_loups.t_constats SET dans_aa=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=20;
 END IF;
 RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
CREATE TRIGGER update_geom AFTER
insert or update of the_geom_point
on constats_loups.t_constats for each row execute procedure constats_loups.update_com_sec();

CREATE OR REPLACE FUNCTION constats_loups.update_com_sec_d()
  RETURNS trigger AS
$BODY$
 DECLARE
 geom_change boolean; 
BEGIN
 geom_change = false;
 IF(TG_OP ='UPDATE') THEN
    SELECT INTO geom_change NOT ST_EQUALS(OLD.geom, NEW.geom);
 END IF;
 IF(TG_OP='INSERT' OR (TG_OP='UPDATE' AND geom_change)) THEN
    UPDATE constats_loups.t_constats_declaratifs SET id_secteur_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=30 and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats_declaratifs SET id_commune_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.id_type=25 and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats_declaratifs SET departement_d=substring(ref_geo.l_areas.area_code from 1 for 2) from ref_geo.l_areas where id_commune_d=ref_geo.l_areas.id_area;
    UPDATE constats_loups.t_constats_declaratifs SET dans_coeur_d=ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=1;
    UPDATE constats_loups.t_constats_declaratifs SET dans_aa_d=ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom) from ref_geo.l_areas WHERE ref_geo.l_areas.id_type=20;
 END IF;
 RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
CREATE TRIGGER update_geom_d AFTER
insert or update of geom
 on constats_loups.t_constats_declaratifs for each row execute procedure constats_loups.update_com_sec_d();