CREATE SCHEMA IF NOT EXISTS constats_loups;

DROP TABLE IF EXISTS constats_loups.t_constats;
CREATE TABLE constats_loups.t_constats
(
  id_constat serial NOT NULL,
  date_attaque date,
  date_constat date,
  nom_agent1 character varying,
  nom_agent2 character varying,
  proprietaire character varying,
  type_animaux character varying,
  nb_victimes_mort integer,
  nb_victimes_blesse integer,
  statut character varying(7),
  type_animaux character varying(20),
  nb_victimes_mortes integer,
  nb_victimes_blessees integer,
  statut character varying(20),
  the_geom_point geometry(Point,2154),
  CONSTRAINT t_constats_pkey PRIMARY KEY (id_constat)
);

-- Données exemple
INSERT INTO constats_loups.t_constats(date_attaque,date_constat,nom_agent1,nom_agent2,proprietaire,type_animaux,nb_victimes_mort,nb_victimes_blesse,statut,the_geom_point) VALUES
('2020-04-18','2020-04-20','agent 1','agent 2','Berger 1','bovins',3,4,'attente',ST_transform(ST_geometryFromText('POINT(6.30630 44.84194)',4326),2154)),
('2020-05-01','2020-05-04','agent 1','agent 3','Berger 2','caprins',2,6,'attente',ST_transform(ST_geometryFromText('POINT(5.9477 44.9602)',4326),2154));
--UPDATE t_constats SET the_geom_point=ST_transform(geom_4326,2154);

--select ST_asText(the_geom_point)from t_constats;

--select ST_asText(the_geom_point)from t_constats;
