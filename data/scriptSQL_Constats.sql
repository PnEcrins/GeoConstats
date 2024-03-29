--Schema constats_loups

CREATE SCHEMA IF NOT EXISTS constats_loups;

--Tables bib pour le type_animaux et le statut

CREATE TABLE constats_loups.bib_type_animaux
(
  id integer NOT NULL,
  nom character varying(7),
  CONSTRAINT animauxpkey PRIMARY KEY (id)
);

CREATE TABLE constats_loups.bib_statut
(
  id integer NOT NULL,
  nom character varying(10),
  CONSTRAINT statutpkey PRIMARY KEY (id)
);

--Fonctions pour les triggers de maj des données issues de la geometrie

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
    UPDATE constats_loups.t_constats 
      SET id_secteur=ref_geo.l_areas.id_area 
      FROM ref_geo.l_areas a 
      JOIN ref_geo.bib_areas_types b ON b.id_type = a.id_type
      WHERE id_constat = NEW.id_constat AND b.type_code = 'SEC' and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats 
      SET id_commune=ref_geo.l_areas.id_area 
      FROM ref_geo.l_areas 
      JOIN ref_geo.bib_areas_types b ON b.id_type = a.id_type
      WHERE id_constat = NEW.id_constat AND b.type_code = 'COM' and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats 
      SET id_departement=ref_geo.l_areas.id_area 
      from ref_geo.l_areas 
      JOIN ref_geo.bib_areas_types b ON b.id_type = a.id_type
      where id_constat = NEW.id_constat AND b.type_code = 'DEP' and ST_Within(constats_loups.t_constats.the_geom_point,ref_geo.l_areas.geom);
    UPDATE constats_loups.t_constats 
      SET dans_coeur=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) 
      from ref_geo.l_areas 
      JOIN ref_geo.bib_areas_types b ON b.id_type = a.id_type
      WHERE id_constat = NEW.id_constat AND b.type_code = 'ZC';
    UPDATE constats_loups.t_constats 
    SET dans_aa=ST_Within(NEW.the_geom_point,ref_geo.l_areas.geom) 
    from ref_geo.l_areas 
    JOIN ref_geo.bib_areas_types b ON b.id_type = a.id_type
    WHERE id_constat = NEW.id_constat AND b.type_code = 'AA';
 END IF;
 RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


-- table t_constats

--DROP TABLE IF EXISTS constats_loups.t_constats;
CREATE TABLE constats_loups.t_constats
(
  id_constat serial NOT NULL,
  date_attaque date NOT NULL,
  date_constat date NOT NULL,
  nom_agent1 character varying,
  nom_agent2 character varying,
  proprietaire character varying,
  nb_victimes_mort integer,
  nb_victimes_blesse integer,
  nb_disparus integer,
  nb_indemnises integer,
  statut integer,
  type_animaux integer,
  the_geom_point geometry(Point,2154),
  id_secteur integer,
  id_commune integer,
  nb_jour_agent real,
  id_departement integer,
  id_role integer,
  dans_coeur boolean,
  dans_aa boolean,
  comment text,
  declaratif boolean,
  CONSTRAINT t_constats_pkey PRIMARY KEY (id_constat),
  CONSTRAINT animaux_fkey FOREIGN KEY (type_animaux)
      REFERENCES constats_loups.bib_type_animaux (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT commune_fkey FOREIGN KEY (id_commune)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT role_fkey FOREIGN KEY (id_role)
      REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT secteur_fkey FOREIGN KEY (id_secteur)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT dep_fkey FOREIGN KEY (id_departement)
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
