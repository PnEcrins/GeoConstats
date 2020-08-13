---------------------------------------------------- DONNEES EXEMPLE----------------------------------------------
--Schema constats_loups
--bib_statut
INSERT INTO constats_loups.bib_statut(id,nom) VALUES (1,'En attente');
INSERT INTO constats_loups.bib_statut(id,nom) VALUES (2,'Rejeté');
INSERT INTO constats_loups.bib_statut(id,nom) VALUES(3,'Indemnisé');
--bib_type_animaux
INSERT INTO constats_loups.bib_type_animaux(id,nom) VALUES (1,'Ovins');
INSERT INTO constats_loups.bib_type_animaux(id,nom) VALUES(2,'Bovins');
INSERT INTO constats_loups.bib_type_animaux(id,nom) VALUES(3,'Caprins');
--t_constats
INSERT INTO constats_loups.t_constats(date_attaque,date_constat,nom_agent1,nom_agent2,proprietaire,type_animaux,nb_victimes_mort,nb_victimes_blesse,statut,the_geom_point,id_role) VALUES
('2020-04-18','2020-04-20','agent 1','agent 2','Berger 1',2,3,4,1,ST_transform(ST_geometryFromText('POINT(6.30630 44.84194)',4326),2154),1),
('2020-05-01','2020-05-04','agent 1','agent 3','Berger 2',1,2,6,1,ST_transform(ST_geometryFromText('POINT(5.9477 44.9602)',4326),2154),2);
--t_constats_declaratifs

INSERT INTO constats_loups.t_constats_declaratifs (date_attaque_d, date_constat_d, lieu_dit, proprietaire_d, type_animaux_d, nb_victimes_mort_d, nb_victimes_blesse_d, statut_d, geom,id_role) VALUES ('2020-06-05', '2020-06-11', 'Les Têtes', NULL, 3, 1, NULL, 3, '01010000206A0800001ED9175372E22D41FBB64D86E37A5841',1);
INSERT INTO constats_loups.t_constats_declaratifs (date_attaque_d, date_constat_d, lieu_dit, proprietaire_d, type_animaux_d, nb_victimes_mort_d, nb_victimes_blesse_d, statut_d, geom,id_role) VALUES ('2020-06-09', '2020-06-11', 'La Salce', NULL, 1, 1, NULL, 3, '01010000206A0800008A56101AA1B72D41BF19DCCB9C795841',2);
INSERT INTO constats_loups.t_constats_declaratifs (date_attaque_d, date_constat_d, lieu_dit, proprietaire_d, type_animaux_d, nb_victimes_mort_d, nb_victimes_blesse_d, statut_d, geom,id_role) VALUES ('2020-06-30', '2020-06-30', 'Palluel', NULL, 1, 1, NULL, 1, '01010000206A080000FBA841B1BCA62D41ED80AA00F6725841',2);