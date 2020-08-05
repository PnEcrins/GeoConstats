
---------------------------------------------------- DONNEES EXEMPLE----------------------------------------------

INSERT INTO utilisateurs.t_applications (id_application, code_application, nom_application, desc_application, id_parent) VALUES 
(2, 'GC', 'GeoConstats', 'Application permettant d''administrer les constats d''attaques de loups.', NULL)
;

INSERT INTO utilisateurs.cor_profil_for_app (id_profil, id_application) VALUES
(6, 2)
,(3, 2)
,(2,2)
;
INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, email, date_insert, date_update, id_organisme, remarques, pass_plus) VALUES 
(false, 6, 'référent', 'référent', 'test', NULL, 'Blabla', NULL, NULL, NULL, -1, 'utilisateur test à modifier ou supprimer', NULL)
;
INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil) VALUES
(9, 1, 6),
(9, 2, 6),
(6, 2, 2)
;