---------------------------------------------------- DONNEES EXEMPLE----------------------------------------------

INSERT INTO utilisateurs.t_applications (id_application, code_application, nom_application, desc_application, id_parent) VALUES 
(2, 'GC', 'GeoConstats', 'Application permettant d''administrer les constats d''attaques de loups.', NULL)
;

INSERT INTO utilisateurs.cor_profil_for_app (id_profil, id_application) VALUES
(6, 2)
,(3, 2)
,(2,2)
;
INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, pass_plus, date_insert, date_update, id_organisme, remarques) VALUES 
(false, 6, 'referent', 'référent', 'test', NULL, '21232f297a57a5a743894a0e4a801fc3', '$2y$13$TMuRXgvIg6/aAez0lXLLFu0lyPk4m8N55NDhvLoUHh/Ar3rFzjFT.', NULL, NULL, -1, 'utilisateur test à modifier ou supprimer')
;
INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil) VALUES
(6, 2, 6),
(9, 2, 6),
(7, 2, 2)
;