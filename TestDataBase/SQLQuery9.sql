-- Pas 1: Schimbă la baza de date
USE GestiuneDocumente;
GO

-- Pas 2: Șterge tabelele existente (în ordinea corectă din cauza foreign keys)
IF OBJECT_ID('dbo.Documente', 'U') IS NOT NULL
    DROP TABLE dbo.Documente;

IF OBJECT_ID('dbo.Persoane', 'U') IS NOT NULL
    DROP TABLE dbo.Persoane;

IF OBJECT_ID('dbo.TipuriDocumente', 'U') IS NOT NULL
    DROP TABLE dbo.TipuriDocumente;
GO

-- Pas 3: Recreează tabelele cu structura corectă
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
    numar_document NVARCHAR(255), -- Am mărit dimensiunea pentru app.py
    data_emitere DATE,
    descriere NVARCHAR(MAX), -- Am mărit pentru app.py
    FOREIGN KEY (id_tip) REFERENCES TipuriDocumente(id_tip),
    FOREIGN KEY (id_persoana) REFERENCES Persoane(id_persoana)
);
GO

-- Pas 4: Inserează datele de test
INSERT INTO TipuriDocumente (denumire) VALUES 
    ('Adeverință'), 
    ('Contract'), 
    ('Certificat'),
    ('Document General'); -- Pentru app.py

INSERT INTO Persoane (nume, prenume) VALUES 
    ('Popescu', 'Ion'), 
    ('Ionescu', 'Maria'),
    ('Administrator', 'Sistem'); -- Pentru app.py

INSERT INTO Documente (id_tip, id_persoana, numar_document, data_emitere, descriere)
VALUES 
    (1, 1, 'DOC001', '2024-01-15', 'Adeverință medicală'),
    (2, 2, 'DOC002', '2023-11-22', 'Contract de voluntariat');
GO

-- Pas 5: Verifică rezultatul
SELECT 'Baza de date recreată cu succes!' AS Status;

SELECT d.id_document, d.numar_document, d.data_emitere, d.descriere, 
       td.denumire as tip_document, p.nume, p.prenume
FROM Documente d
LEFT JOIN TipuriDocumente td ON d.id_tip = td.id_tip
LEFT JOIN Persoane p ON d.id_persoana = p.id_persoana;

-- Verifică structura tabelelor
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN ('TipuriDocumente', 'Persoane', 'Documente')
ORDER BY TABLE_NAME, ORDINAL_POSITION;