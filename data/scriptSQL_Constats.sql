--Schema constats_loups

CREATE SCHEMA IF NOT EXISTS constats_loups;

--Tables bib pour le type_animaux et le statut

CREATE TABLE constats_loups.bib_type_animaux
(
  id serial NOT NULL,
  nom character varying(7),
  CONSTRAINT animauxpkey PRIMARY KEY (id)
);

CREATE TABLE constats_loups.bib_statut
(
  id serial NOT NULL,
  nom character varying(10),
  CONSTRAINT statutpkey PRIMARY KEY (id)
);

--Fonctions pour les triggers de maj des secteurs et communes

CREATE OR REPLACE FUNCTION constats_loups.update_com_sec()
 RETURNS TRIGGER AS $BODY$
 DECLARE
 geom_change boolean; 
BEGIN
 geom_change = false;
 IF(TG_OP ='UPDATE') THEN
     SELECT INTO geom_change NOT ST_EQUALS(OLD.the_geom_point, NEW.the_geom_point);
 END IF;
 IF(TG_OP='INSERT' OR (TG_OP='UPDATE' AND geom_change)) THEN
    UPDATE constats_loups.t_constats SET id_secteur=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.area_code='SEC' and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats SET id_commune=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.area_code='COM' and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
 END IF;
 RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION constats_loups.update_com_sec_d()
 RETURNS TRIGGER AS $BODY$
 DECLARE
 geom_change boolean; 
BEGIN
 geom_change = false;
 IF(TG_OP ='UPDATE') THEN
    SELECT INTO geom_change NOT ST_EQUALS(OLD.geom, NEW.geom);
 END IF;
 IF(TG_OP='INSERT' OR (TG_OP='UPDATE' AND geom_change)) THEN
    UPDATE constats_loups.t_constats_declaratifs SET id_secteur_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.area_code='SEC' and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats_declaratifs SET id_commune_d=ref_geo.l_areas.id_area FROM ref_geo.l_areas WHERE ref_geo.l_areas.area_code='COM' and ST_Within(constats_loups.t_constats_declaratifs.geom,ref_geo.l_areas.geom);
 END IF;
 RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

-- table t_constats

--DROP TABLE IF EXISTS constats_loups.t_constats;
CREATE TABLE constats_loups.t_constats
(
  id_constat serial NOT NULL,
  date_attaque date,
  date_constat date,
  nom_agent1 character varying,
  nom_agent2 character varying,
  proprietaire character varying,
  nb_victimes_mort integer,
  nb_victimes_blesse integer,
  statut integer,
  type_animaux integer,
  the_geom_point geometry(Point,2154),
  id_secteur integer,
  id_commune integer,
  nb_jour_agent real,
  departement character varying(2),
  CONSTRAINT t_constats_pkey PRIMARY KEY (id_constat),
  CONSTRAINT animaux_fkey FOREIGN KEY (type_animaux)
      REFERENCES constats_loups.bib_type_animaux (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT secteur_fkey FOREIGN KEY (id_secteur)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT statut_fkey FOREIGN KEY (statut)
      REFERENCES constats_loups.bib_statut (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TRIGGER update_geom AFTER
insert or update of the_geom_point
on constats_loups.t_constats for each row execute procedure constats_loups.update_com_sec();

-- table t_constats_declaratifs

CREATE TABLE constats_loups.t_constats_declaratifs
(
  id_constat_d serial NOT NULL,
  date_attaque_d date,
  date_constat_d date,
  lieu_dit character varying,
  proprietaire_d character varying,
  type_animaux_d integer,
  nb_victimes_mort_d integer,
  nb_victimes_blesse_d integer,
  statut_d integer,
  geom geometry(Point,2154),
  id_secteur_d integer,
  id_commune_d integer,
  departement_d character varying(2),
  CONSTRAINT decla_pkey PRIMARY KEY (id_constat_d),
  CONSTRAINT t_constats_declaratifs_id_secteur_d_fkey FOREIGN KEY (id_secteur_d)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT t_constats_declaratifs_statut_d_fkey FOREIGN KEY (statut_d)
      REFERENCES constats_loups.bib_statut (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT t_constats_declaratifs_type_animaux_d_fkey FOREIGN KEY (type_animaux_d)
      REFERENCES constats_loups.bib_type_animaux (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TRIGGER update_geom_d AFTER
insert or update of geom
 on constats_loups.t_constats_declaratifs for each row execute procedure constats_loups.update_com_sec_d();
