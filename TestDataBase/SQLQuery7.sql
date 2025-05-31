INSERT INTO TipuriDocumente (denumire) VALUES ('Adeverință'), ('Contract'), ('Certificat');

INSERT INTO Persoane (nume, prenume) VALUES ('Popescu', 'Ion'), ('Ionescu', 'Maria');

INSERT INTO Documente (id_tip, id_persoana, numar_document, data_emitere, descriere)
VALUES (1, 1, 'DOC001', '2024-01-15', 'Adeverință medicală'),
       (2, 2, 'DOC002', '2023-11-22', 'Contract de voluntariat');
