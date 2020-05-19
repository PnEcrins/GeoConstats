drop table constats;
CREATE TABLE constats
(
  id serial NOT NULL,
  date_attaque date,
  date_constat date,
  nom_agent1 character varying,
  nom_agent2 character varying,
  proprietaire character varying,
  type_animaux character varying,
  nb_victimes_mort integer,
  nb_victimes_blesse integer,
  situation character varying(7),
  CONSTRAINT constats_pkey PRIMARY KEY (id)
);
SELECT AddGeometryColumn('constats', 'geometry', 2154, 'POINT',2);
SELECT AddGeometryColumn('constats', 'geom_4326', 4326, 'POINT',2);
INSERT INTO constats(id,date_attaque,date_constat,nom_agent1,nom_agent2,proprietaire,type_animaux,nb_victimes_mort,nb_victimes_blesse,situation,geom_4326) VALUES
(1,'2020-04-18','2020-04-20','agent 1','agent 2','Berger 1','bovins',3,4,'attente',ST_geometryFromText('POINT(6.30630 44.84194)',4326)),
(2,'2020-05-01','2020-05-04','agent 1','agent 3','Berger 2','caprins',2,6,'attente',ST_geometryFromText('POINT(5.9477 44.9602)',4326));


update constats set geometry=ST_transform(geom_4326,2154);

#select ST_asText(geometry)from constats;
select dateAttaque from constats;