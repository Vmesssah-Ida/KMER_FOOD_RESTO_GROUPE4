DROP DATABASE IF EXISTS Restaurant;
CREATE DATABASE Restaurant CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE Restaurant;
/* ===================== TABLES ===================== */
CREATE TABLE Client (
 id_Client INT PRIMARY KEY,
 Nom VARCHAR(20),
 Prenom VARCHAR(20),
 Tel VARCHAR(15),
 Email VARCHAR(45),
 Type_de_Client VARCHAR(20)
);
CREATE TABLE `Table` (
 id_Table INT PRIMARY KEY,
 Numero_Table VARCHAR(3),
 Capacite INT,
 Commentaire TEXT
);
CREATE TABLE Reservation (
 id_Reservation INT PRIMARY KEY,
 id_Client INT,
 id_Table INT,
 `Date` DATE,
 Heure TIME,
 Statut VARCHAR(45),
 FOREIGN KEY (id_Client) REFERENCES Client(id_Client),
 FOREIGN KEY (id_Table) REFERENCES `Table`(id_Table)
);
CREATE TABLE Ingredient (
 id_Ingredient INT PRIMARY KEY,
 Nom VARCHAR(45),
 Unite_de_Mesure VARCHAR(45),
 `Type` VARCHAR(30)
);
CREATE TABLE Employe (
 id_Employe INT PRIMARY KEY,
 Nom VARCHAR(20),
 Prenom VARCHAR(20),
 Tel VARCHAR(15),
 Salaire INT,
 Date_Embauche DATE
);
CREATE TABLE Produit (
 id_Produit INT PRIMARY KEY,
 id_Createur INT,
 Nom VARCHAR(30),
 `Description` VARCHAR(45),
 Duree_Cuisson VARCHAR(20),
 Nombre_Personnes INT,
 FOREIGN KEY (id_Createur) REFERENCES Employe(id_Employe)
);
CREATE TABLE Stock (
 id_Ingredient INT PRIMARY KEY,
 Quantite_Actuelle DECIMAL(10,2),
 Seuil_Alerte DECIMAL(10,2),
 FOREIGN KEY (id_Ingredient) REFERENCES Ingredient(id_Ingredient)
);
CREATE TABLE Variation_Stock (
 id_Variation INT PRIMARY KEY,
 id_Ingredient INT,
 `Date` DATE,
 `Type` VARCHAR(10),
 Quantite DECIMAL(10,2),
 FOREIGN KEY (id_Ingredient) REFERENCES Ingredient(id_Ingredient)
);
CREATE TABLE Composition_Produit (
 id_Produit INT,
 id_Ingredient INT,
 Quantite_Utilisee DECIMAL(10,2),
 PRIMARY KEY (id_Produit, id_Ingredient),
 FOREIGN KEY (id_Produit) REFERENCES Produit(id_Produit),
 FOREIGN KEY (id_Ingredient) REFERENCES Ingredient(id_Ingredient)
);
CREATE TABLE Fournisseur (
 id_Fournisseur INT PRIMARY KEY,
 Nom VARCHAR(45),
 Tel VARCHAR(15),
 Adresse VARCHAR(45)
);
CREATE TABLE Poste (
 id_Poste INT PRIMARY KEY,
 Libelle_Poste VARCHAR(45)
);
CREATE TABLE Affectation (
 id_Employe INT,
 id_Poste INT,
 Date_debut DATE,
 Date_fin DATE,
 PRIMARY KEY (id_Employe, id_Poste),
 FOREIGN KEY (id_Employe) REFERENCES Employe(id_Employe),
 FOREIGN KEY (id_Poste) REFERENCES Poste(id_Poste)
);
CREATE TABLE Supervision (
id_Superviseur INT,
 id_Employe INT,
 Date_debut DATE,
 Date_fin DATE,
 PRIMARY KEY (id_Superviseur, id_Employe),
 FOREIGN KEY (id_Superviseur) REFERENCES Employe(id_Employe),
 FOREIGN KEY (id_Employe) REFERENCES Employe(id_Employe)
);
CREATE TABLE Vehicule (
 id_Vehicule INT PRIMARY KEY,
 Immatriculation VARCHAR(15),
 Modele VARCHAR(20),
 Marque VARCHAR(20)
);
CREATE TABLE Deplacement (
 id_Deplacement INT PRIMARY KEY,
id_Chauffeur INT,
 id_Vehicule INT,
 Date_depart DATETIME,
 Destination TEXT,
 Distance_totale DECIMAL(10,2),
 FOREIGN KEY (id_Chauffeur) REFERENCES Employe(id_Employe),
 FOREIGN KEY (id_Vehicule) REFERENCES Vehicule(id_Vehicule)
);
 
 CREATE TABLE Approvisionnement (
 id_Approvisionnement INT PRIMARY KEY,
 id_Ingredient INT,
 id_Fournisseur INT,
 id_Deplacement INT,
 `Date` DATE,
 Quantite DECIMAL(10,2),
 Prix_Unitaire INT,
 FOREIGN KEY (id_Ingredient) REFERENCES Ingredient(id_Ingredient),
 FOREIGN KEY (id_Fournisseur) REFERENCES Fournisseur(id_Fournisseur),
 FOREIGN KEY (id_Deplacement) REFERENCES Deplacement(id_Deplacement)
);
 
CREATE TABLE Equipement (
 id_Equipement INT PRIMARY KEY,
 Nom VARCHAR(45),
 Etat VARCHAR(45),
 Date_Achat DATE
);
CREATE TABLE Maintenance (
 id_Maintenance INT PRIMARY KEY,
 id_Technicien INT,
 id_Equipement INT,
 Date DATE,
 Type VARCHAR(45),
 Commentaire TEXT,
 FOREIGN KEY (id_Technicien) REFERENCES Employe(id_Employe),
 FOREIGN KEY (id_Equipement) REFERENCES Equipement(id_Equipement)
);
CREATE TABLE Action_Marketing (
 id_Action INT PRIMARY KEY,
 id_Responsable INT,
 Type_Action VARCHAR(20),
 `Description` TEXT,
 Date_debut DATE,
 Date_fin DATE,
 Budget INT,
FOREIGN KEY (id_Responsable) REFERENCES Employe(id_Employe)
);
CREATE TABLE Commande (
 id_Commande INT PRIMARY KEY,
id_Client INT,
 `Date` DATETIME,
 Type VARCHAR(30),
 Montant_Total INT,
 Mode_de_Paiement VARCHAR(45),
 FOREIGN KEY (id_Client) REFERENCES Client(id_Client)
);
CREATE TABLE Ligne_Commande (
 id_Commande INT,
 id_Produit INT,
 Quantite DECIMAL(10,2),
 Prix_Unitaire INT,
 PRIMARY KEY (id_Commande, id_Produit),
 FOREIGN KEY (id_Commande) REFERENCES Commande(id_Commande),
 FOREIGN KEY (id_Produit) REFERENCES Produit(id_Produit)
);
CREATE TABLE Livraison (
 id_Livraison INT PRIMARY KEY,
 id_Commande INT UNIQUE,
 id_Deplacement INT,
 FOREIGN KEY (id_Commande) REFERENCES Commande(id_Commande),
 FOREIGN KEY (id_Deplacement) REFERENCES Deplacement(id_Deplacement)
);
CREATE TABLE Facture (
 id_Facture INT PRIMARY KEY,
 `Date` DATE,
 Montant INT,
 `Type` VARCHAR(45)
);
/* ===================== INSERTIONS ===================== */
/* CLIENT */
INSERT INTO Client VALUES
(1,'Ngono','Patrick','699112233','patrick@gmail.com','Particulier'),
(2,'Tchoumi','Brigitte','677889900','brigitte@yahoo.fr','Entreprise'),
(3,'Essono','Marc','695443322','marc@gmail.com','Particulier'),
(4,'Manga','Alice','674556677','alice@gmail.com','Particulier'),
(5,'Kamdem','Paul','698887766','paul@gmail.com','Entreprise'),
(6,'Fopa','Franck','687531512','franckfopa875@gmail.com','Particulier'),
(7,'Djeutoga','Nelson','691120602','ndjeutogatofeun@gmail.com','Particulier'),
(8,'Payne','Success','672506316','successpayne07@gmail.com','Particulier'),
(9,'Wouaba','Brayan','687654144','wouabab@gmail.com','Particulier');
/* TABLE */
INSERT INTO `Table` VALUES
(1,'T1',4,'Fenêtre'),
(2,'T2',6,'VIP'),
(3,'T3',2,'Couple'),
(4,'T4',8,'Famille'),
(5,'T5',4,'Standard');
/* RESERVATION */
INSERT INTO Reservation VALUES
(1,1,1,'2025-01-10','19:00','Confirmée'),
(2,2,2,'2025-01-11','20:00','Confirmée'),
(3,3,3,'2025-01-12','18:30','Annulée'),
(4,4,4,'2025-01-13','19:30','Confirmée'),
(5,5,5,'2025-01-14','20:15','Confirmée');
/* EMPLOYE */
INSERT INTO Employe VALUES
(1,'Fokou','Alain','699887766',210000,'2022-06-01'),
(2,'Mballa','Serge','677445566',150000,'2023-11-15'),
(3,'Essomba','Jean','696554433',150000,'2024-03-20'),
(4,'Nguefack','Linda','655778899',80000,'2024-02-10'),
(5,'Tchoua','Patrick','670998877',100000,'2024-07-01'),
(6,'Pokam','Justin','677809865',80000,'2022-09-06'),
(7,'Kenfack','Paul','672801865',120000,'2022-01-06'),
(8,'Fotso','Mirielle','655879034',85000,'2022-02-23'),
(9,'Ngo','Alice','655833031',85000,'2022-02-24'),
(10,'Njing','Ella','655119030',85000,'2022-02-23'),
(11,'Kameni','Diane','685829131',85000,'2022-02-26'),
(12,'Tchuene','Eric','675879047',95000,'2022-02-20'),
(13,'Ousmane','Bakary','675449044',90000,'2022-02-28'),
(14,'Talla','Jean-Luc','675867041',105000,'2022-02-01'),
(15,'Nyimen','Anderson','675060048',70000,'2022-02-01'),
(16,'Asha','Maeva','681603279',50000,'2022-01-01'),
(17,'Zogo', 'Brice', '690112233', 70000, '2023-02-01'),
(18,'Zanga','Merlin','690551403',130000,'2024-03-20');
/* PRODUIT */
INSERT INTO Produit VALUES
(1,2,'Poulet DG','Plat','2 heures',3),
(2,2,'Ndolé','Plat','2 heures',4),
(3,2,'Riz sauté','Plat','1 heure',3),
(4,3,'Jus de Gingembre','Boisson','45 minutes',2),
(5,3,'Jus de Bissap','Boisson','30 minutes',2);
/* INGREDIENT */
INSERT INTO Ingredient VALUES 
(1, 'Poulet', 'Kg', 'Protéine'),
(2, 'Arachide', 'Kg', 'Léagineux'),
(3, 'Riz', 'Kg', 'Féculent'),
(4, 'Gingembre', 'Kg', 'Plante / Épice'),
(5, 'Bissap', 'Kg', 'Plante / Épice'),
(6, 'Tomates', 'Kg', 'Légume'),
(7, 'Plantain', 'Regime', 'Féculent'),
(8, 'Huile de Soja', 'Litre', 'Léagineux'),
(9, 'Viande de Boeuf', 'Kg', 'Protéine'),
(10, 'Sel', 'Kg', 'Épicerie'),
(11, 'Oignons', 'Kg', 'Légume'),
(12, 'Poivrons', 'Kg', 'Légume'),
(13, 'Poisson fumé', 'Kg', 'Protéine'),
(14, 'Crevettes séchées', 'Kg', 'Épicerie'),
(15, 'Cube d''assaisonnement', 'Paquet', 'Épicerie'),
(16, 'Ail & Gingembre moulu', 'Kg', 'Plante / Épice'),
(17, 'Sucre', 'Kg', 'Épicerie');
/* STOCK */
INSERT INTO Stock VALUES
(1,30,5),
(2,20,4),
(3,50,10),
(4,15,3),
(5,18,4),
(6, 10, 2),  
(7, 15, 5), 
(8, 20, 5), 
(9, 25, 5),  
(10, 5, 1),
(11, 15, 3),   
(12, 10, 2),  
(13, 8, 2),    
(14, 5, 1),    
(15, 20, 5),  
(16, 3, 1),    
(17, 25, 5);
/* VARIATION_STOCK */
INSERT INTO Variation_Stock VALUES
(1,1,'2025-01-05','entrée',20),
(2,2,'2025-01-07','entrée',5),
(3,3,'2025-01-10','sortie',25),
(4,4,'2025-01-12','entrée',2),
(5,5,'2025-01-14','sortie',3);

/* COMPOSITION PRODUIT */
-- POULET DG 
INSERT INTO Composition_Produit (id_Produit, id_Ingredient, Quantite_Utilisee) VALUES 
(1, 1, 0.5),   
(1, 7, 0.25),  
(1, 8, 0.15),  
(1, 6, 0.1),   
(1, 11, 0.05), 
(1, 12, 0.05), 
(1, 15, 0.02); 

-- NDOLÉ 
INSERT INTO Composition_Produit (id_Produit, id_Ingredient, Quantite_Utilisee) VALUES 
(2, 2, 0.4),   
(2, 9, 0.3),   
(2, 8, 0.1),   
(2, 13, 0.1),  
(2, 14, 0.05), 
(2, 11, 0.05), 
(2, 10, 0.01); 

-- RIZ SAUTÉ 
INSERT INTO Composition_Produit (id_Produit, id_Ingredient, Quantite_Utilisee) VALUES 
(3, 3, 0.3),  
(3, 8, 0.05),  
(3, 6, 0.1),   
(3, 11, 0.05), 
(3, 9, 0.1),   
(3, 10, 0.01); 

-- JUS DE GINGEMBRE 
INSERT INTO Composition_Produit (id_Produit, id_Ingredient, Quantite_Utilisee) VALUES 
(4, 4, 0.15),  
(4, 17, 0.1);  

-- JUS DE BISSAP 
INSERT INTO Composition_Produit (id_Produit, id_Ingredient, Quantite_Utilisee) VALUES 
(5, 5, 0.1),   
(5, 17, 0.1);  

/* FOURNISSEUR */
INSERT INTO Fournisseur VALUES
(1,'Marché Central','677112233','Yaoundé'),
(2,'Mokolo Vivres','699223344','Yaoundé'),
(3,'Agro Bafoussam','655667788','Bafoussam'),
(4,'Fresh Douala','690112233','Douala'),
(5,'Bio Camer','698887755','Yaoundé');
/* POSTE */
INSERT INTO Poste VALUES
(1,'Cuisinier'),
(2,'Serveur'),
(3,'Technicien'),
(4,'Chauffeur'),
(5,'Agent de Marketing'),
(6,'Directeur General'),
(7,'Chef Cuisinier'),
(8,'Chef du Magasin'),
(9,'Comptable'),
(10,'Responsable des Achats'),
(11,'Gestionnaire de Stock'),
(12,'Agent Téléphonique'),
(13,'Agent de Sécurité');
/* AFFECTATION */
INSERT INTO Affectation VALUES
(1,6,'2022-06-01',NULL),
(2,7,'2023-11-15',NULL),
(3,7,'2024-03-20',NULL),
(4,2,'2024-02-10',NULL),
(5,5,'2024-07-01',NULL),
(6,4,'2024-09-06',NULL),
(7,3,'2022-01-06',NULL),
(8,1,'2022-02-23',NULL),
(9,1,'2022-04-24',NULL),
(10,1,'2022-02-23',NULL),
(11,1,'2022-02-26',NULL),
(12,8,'2022-02-20',NULL),
(13,9,'2022-02-28',NULL),
(14,11,'2022-02-01',NULL),
(15,10,'2022-02-01',NULL),
(16,12,'2022-01-01',NULL),
(17,13,'2023-02-01',NULL),
(18,4,'2023-02-01',NULL);

/* SUPERVISION */
INSERT INTO Supervision VALUES
(8,2,'2022-02-23',NULL),
(9,2,'2022-04-24',NULL),
(10,3,'2022-02-23',NULL),
(11,3,'2022-02-26',NULL),
(6,6,'2022-01-01',NULL),
(14,12,'2022-02-01',NULL);
/* VEHICULE */
INSERT INTO Vehicule VALUES
(1,'LT-456-CM','Hilux','Toyota'),
(2,'CE-982-YA','Sprinter','Mercedes'),
(3,'LT-221-CE','D-Max','Isuzu'),
(4,'SW-889-LT','Hiace','Toyota'),
(5,'CE-101-YA','Transit','Ford');
/* DEPLACEMENT */
INSERT INTO Deplacement VALUES
(1,18,1,'2025-01-05 08:00','Marché Central',12.5),
(2,18,2,'2025-01-07 06:45','Nsam',18),
(3,6,3,'2025-01-10 09:30','Mokolo',9.2),
(4,18,4,'2025-01-12 07:15','Ekounou',14.8),
(5,18,5,'2025-01-15 10:00','Bastos',6.4),
(6,6,3,'2025-11-10 19:30','Mimboman',9.2),
(7,18,2,'2025-10-12 10:30','Nkoabang',6.4);
/* APPROVISIONNEMENT */
INSERT INTO Approvisionnement VALUES
(1,1,1,3,'2025-01-05',20,2500),
(2,2,2,3,'2025-01-07',15,1800),
(3,3,3,3,'2025-01-10',25,600),
(4,4,4,3,'2025-01-12',10,1200),
(5,5,5,3,'2025-01-15',12,1000);
/* EQUIPEMENT */
INSERT INTO Equipement VALUES
(1,'Four','Fonctionnel','2023-05-10'),
(2,'Congélateur','Fonctionnel','2022-11-20'),
(3,'Mixeur','En panne','2021-09-15'),
(4,'Réfrigérateur','Fonctionnel','2022-03-08'),
(5,'Hotte','Fonctionnel','2023-01-12');
/* MAINTENANCE */
INSERT INTO Maintenance VALUES
(1,7,3,'2025-01-08','Corrective','Moteur'),
(2,7,1,'2025-01-10','Préventive','Nettoyage'),
(3,7,2,'2025-01-12','Préventive','Contrôle'),
(4,7,4,'2025-01-14','Préventive','Joints'),
(5,7,5,'2025-01-16','Préventive','Filtres');
/* ACTION_MARKETING*/
INSERT INTO Action_Marketing VALUES
(1,5,'Promo Week-end','Promotion','2025-01-05','2025-01-07',50000),
(2,5,'Offre Saint-Valentin','Promotion','2025-02-10','2025-02-14',70000),
(3,5,'Campagne Facebook','Publicité','2025-01-01','2025-01-31',30000),
(4,5,'Happy Hour','Promotion','2025-01-15','2025-01-20',40000),
(5,5,'Menu Étudiant','Promotion','2025-01-08','2025-01-31',25000);
/* COMMANDE */
INSERT INTO Commande VALUES
(1,1,'2025-01-10 19:30','Sur place',6500,'Orange Money'),
(2,2,'2025-11-11 20:00','À livrer',8000,'Espèces'),
(3,3,'2025-01-12 18:45','Sur place',12000,'MTN MoMo'),
(4,4,'2025-11-13 19:00','Sur place',9000,'Espèces'),
(5,5,'2025-01-14 20:15','À livrer',9800,'Orange Money'),
(6,4,'2025-11-13 19:30','À emporter',4500,'Orange Money');
/* LIGNE COMMANDE */
INSERT INTO Ligne_Commande VALUES
(1,1,1,5000),
(1,4,1,1500),
(2,2,1,8000),
(3,1,2,5000),
(3,4,2,1500),
(4,3,2,4500),
(5,5,2,4900),
(6,3,1,4500);
/* LIVRAISON */
INSERT INTO Livraison VALUES
(1,5,4),
(2,2,5);
/* FACTURE */
INSERT INTO Facture VALUES
(1,'2025-01-10',6500,'Facture Client'),
(2,'2025-11-11',8000,'Facture Client'),
(3,'2025-01-12',12000,'Facture Client'),
(4,'2025-11-13',9000,'Facture Client'),
(5,'2025-01-14',9800,'Facture Client'),
(6,'2025-11-13',4500,'Facture Client'),
(7,'2025-01-05',50000,'Achat'),
(8,'2025-01-07',27000,'Achat'),
(9,'2025-01-10',15000,'Achat'),
(10,'2025-01-12',12000,'Achat'),
(11,'2025-01-15',25000,'Achat'),
(12,'2025-01-05',50000,'Marketing'),
(13,'2025-02-10',70000,'Marketing'),
(14,'2025-01-01',30000,'Marketing'),
(15,'2025-01-15',40000,'Marketing'),
(16,'2025-01-08',25000,'Marketing'),
(17,'2025-10-31', 1840000, 'Paiement Salaires Octobre'),
(18,'2025-11-30', 1840000, 'Paiement Salaires Novembre'),
(19,'2025-12-31', 1840000, 'Paiement Salaires Décembre'),
(20,'2023-11-05', 150000, 'Loyer du local - Novembre'),
(21,'2023-11-10', 45000, 'Facture Électricité (Eneo)'),
(22,'2023-11-12', 12000, 'Facture Eau (Camwater)');


/* ============== REQUETES ============== */

SELECT Nom, Adresse FROM Fournisseur ORDER BY id_Fournisseur DESC;

select SUM(Montant_total) as Revenu_Commandes_Sur_Place from Commande where Type = 'Sur place';

Select SUM(Salaire) AS Salaire_Total
FROM Employe;

select e.Nom, e.Prenom, e.Tel, p.Libelle_Poste AS Poste
 FROM Employe e
 JOIN Affectation a ON e.id_Employe=a.id_Employe
 JOIN Poste p ON a.id_Poste = p.id_Poste
 Where a.Date_fin IS NULL;

SELECT DISTINCT
    c.id_Commande,
    i.Nom AS Ingredient,
    c.Montant_Total AS Prix_Commande
FROM Commande c
JOIN Ligne_Commande lc ON c.id_Commande = lc.id_Commande
JOIN Composition_Produit cp ON lc.id_Produit = cp.id_Produit
JOIN Ingredient i ON cp.id_Ingredient = i.id_Ingredient
WHERE i.id_Ingredient IN (
    SELECT cp2.id_Ingredient
    FROM Ligne_Commande lc2
    JOIN Composition_Produit cp2 ON lc2.id_Produit = cp2.id_Produit
    GROUP BY cp2.id_Ingredient
    HAVING COUNT(DISTINCT lc2.id_Commande) > 1
)
ORDER BY i.Nom, c.id_Commande;

Select SUM(Montant_Total) AS Chiffre_Affaires_Novembre_2025
FROM Commande
Where Date >='2025-11-01 00:00:00' AND Date < '2025-12-01 00:00:00';

Select Nom,Prenom,Tel,Email  From Client  where id_client > 5;

