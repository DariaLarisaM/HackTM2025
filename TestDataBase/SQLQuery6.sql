USE GestiuneDocumente;

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
