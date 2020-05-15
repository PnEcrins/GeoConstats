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
INSERT INTO constats(id,date,"nbVictimes",moment,chien,berger,valide,geom_4326) VALUES
(2,'2020-04-20',9,'jour',False,False,'attente',ST_geometryFromText('POINT(6.30630 44.84194)',4326));

#select ST_asText(geometry)from constats;