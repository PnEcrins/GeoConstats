CREATE TABLE constats
(
  id serial NOT NULL,
  date date,
  "nbVictimes" integer,
  moment character varying(4),
  chien boolean,
  berger boolean,
  valide character varying(10),
  CONSTRAINT constats_pkey PRIMARY KEY (id)
)
SELECT AddGeometryColumn('constats', 'geometry', 2154, 'POINT',2);
SELECT AddGeometryColumn('constats', 'geom_4326', 4326, 'POINT',2);
INSERT INTO constats(id,date,"nbVictimes",moment,chien,berger,valide,geometry) VALUES
(1,'2020-04-26',7,'nuit',True,False,'attente',ST_geometryFromText('POINT(6.30830 44.81194)',4326));

#select ST_asText(geometry)from constats;