-- Pas 1: Creează baza de date (dacă nu există)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'GestiuneDocumente')
BEGIN
    CREATE DATABASE GestiuneDocumente;
END
GO

-- Pas 2: Schimbă la baza de date nouă
USE GestiuneDocumente;
GO

-- Pas 3: Creează tabelele
CREATE TABLE TipuriDocumente (
    id_tip INT IDENTITY(1,1) PRIMARY KEY,
    denumire NVARCHAR(100) NOT NULL
);

CREATE TABLE Persoane (
    id_persoana INT IDENTITY(1,1) PRIMARY KEY,
    nume NVARCHAR(100),
    prenume NVARCHAR(100)
);

CREATE TABLE Documente (
    id_document INT IDENTITY(1,1) PRIMARY KEY,
    id_tip INT,
    id_persoana INT,
    numar_document NVARCHAR(50),
    data_emitere DATE,
    descriere NVARCHAR(255),
    FOREIGN KEY (id_tip) REFERENCES TipuriDocumente(id_tip),
    FOREIGN KEY (id_persoana) REFERENCES Persoane(id_persoana)
);
GO

-- Pas 4: Inserează datele de test
INSERT INTO TipuriDocumente (denumire) VALUES ('Adeverință'), ('Contract'), ('Certificat');

INSERT INTO Persoane (nume, prenume) VALUES ('Popescu', 'Ion'), ('Ionescu', 'Maria');

INSERT INTO Documente (id_tip, id_persoana, numar_document, data_emitere, descriere)
VALUES (1, 1, 'DOC001', '2024-01-15', 'Adeverință medicală'),
       (2, 2, 'DOC002', '2023-11-22', 'Contract de voluntariat');
GO

-- Pas 5: Verifică că totul a mers bine
SELECT 'Tabele create cu succes!' AS Status;

SELECT d.id_document, d.numar_document, d.data_emitere, d.descriere, 
       td.denumire as tip_document, p.nume, p.prenume
FROM Documente d
LEFT JOIN TipuriDocumente td ON d.id_tip = td.id_tip
LEFT JOIN Persoane p ON d.id_persoana = p.id_persoana;