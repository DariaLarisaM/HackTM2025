using System;
using System.Data.SqlClient;
using System.IO;             // pentru Directory si File
using System.Diagnostics;    // pentru Process

namespace GestiuneDocumenteApp
{
    class Program
    {
        // Constanta pentru conexiune la baza de date
        const string CONNECTION_STRING = @"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=GestiuneDocumente;Integrated Security=True";

        static void Main(string[] args)
        {
            while (true)
            {
                Console.WriteLine("\nMeniu:");
                Console.WriteLine("1. Adaugă document");
                Console.WriteLine("2. Afisează documente");
                Console.WriteLine("3. Deschide PDF");
                Console.WriteLine("0. Iesire");

                Console.Write("Alege o optiune: ");
                string optiune = Console.ReadLine();

                switch (optiune)
                {
                    case "1":
                        Console.Write("ID tip document: ");
                        int idTip = int.Parse(Console.ReadLine());

                        Console.Write("ID persoană: ");
                        int idPersoana = int.Parse(Console.ReadLine());

                        Console.Write("Număr document: ");
                        string numar = Console.ReadLine();

                        Console.Write("Data emitere (YYYY-MM-DD): ");
                        DateTime dataEmitere = DateTime.Parse(Console.ReadLine());

                        Console.Write("Descriere: ");
                        string descriere = Console.ReadLine();

                        Console.Write("Calea completă către fisierul PDF: ");
                        string caleFisier = Console.ReadLine();

                        AdaugaDocument(idTip, idPersoana, numar, dataEmitere, descriere, caleFisier);
                        break;

                    case "2":
                        AfiseazaDocumente();
                        break;

                    case "3":
                        DeschidePDF();
                        break;

                    case "0":
                        Console.WriteLine("Program închis.");
                        return;

                    default:
                        Console.WriteLine("Opțiune invalidă.");
                        break;
                }
            }
        }

        static void AdaugaDocument(int idTip, int idPersoana, string numar, DateTime dataEmitere, string descriere, string caleSursaFisier)
        {
            string caleFolderPDF = @"D:/HackTM2025/web_app/docs";
            Directory.CreateDirectory(caleFolderPDF); // asigură că folderul există

            string numeFisier = Path.GetFileName(caleSursaFisier);
            string caleDestinatie = Path.Combine(caleFolderPDF, numeFisier);

            File.Copy(caleSursaFisier, caleDestinatie, true); // copie fișierul

            using (SqlConnection conn = new SqlConnection(CONNECTION_STRING))
            {
                conn.Open();
                string query = @"
                    INSERT INTO Documente (id_tip, id_persoana, numar_document, data_emitere, descriere, cale_fisier_pdf)
                    VALUES (@id_tip, @id_persoana, @numar_document, @data_emitere, @descriere, @cale_pdf)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@id_tip", idTip);
                    cmd.Parameters.AddWithValue("@id_persoana", idPersoana);
                    cmd.Parameters.AddWithValue("@numar_document", numar);
                    cmd.Parameters.AddWithValue("@data_emitere", dataEmitere);
                    cmd.Parameters.AddWithValue("@descriere", descriere);
                    cmd.Parameters.AddWithValue("@cale_pdf", caleDestinatie);
                    cmd.ExecuteNonQuery();
                }
            }

            Console.WriteLine("Document adăugat cu succes.");
        }

        static void AfiseazaDocumente()
        {
            using (SqlConnection connection = new SqlConnection(CONNECTION_STRING))
            {
                string query = @"
                    SELECT 
                        d.id_document,
                        td.denumire AS tip_document,
                        p.nume,
                        p.prenume,
                        d.numar_document,
                        d.data_emitere,
                        d.descriere
                    FROM Documente d
                    JOIN TipuriDocumente td ON d.id_tip = td.id_tip
                    JOIN Persoane p ON d.id_persoana = p.id_persoana";

                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    connection.Open();
                    SqlDataReader reader = command.ExecuteReader();

                    Console.WriteLine("DOCUMENTE:");
                    Console.WriteLine(new string('-', 80));

                    while (reader.Read())
                    {
                        Console.WriteLine($"ID: {reader["id_document"]}");
                        Console.WriteLine($"Tip: {reader["tip_document"]}");
                        Console.WriteLine($"Persoană: {reader["nume"]} {reader["prenume"]}");
                        Console.WriteLine($"Număr: {reader["numar_document"]}");
                        Console.WriteLine($"Data: {((DateTime)reader["data_emitere"]).ToShortDateString()}");
                        Console.WriteLine($"Descriere: {reader["descriere"]}");
                        Console.WriteLine(new string('-', 80));
                    }
                }
            }
        }

        static void DeschidePDF()
        {
            Console.Write("Introdu ID-ul documentului pe care vrei să-l deschizi: ");
            if (!int.TryParse(Console.ReadLine(), out int idDocument))
            {
                Console.WriteLine("ID invalid.");
                return;
            }

            using (SqlConnection conn = new SqlConnection(CONNECTION_STRING))
            {
                conn.Open();
                string query = "SELECT cale_fisier_pdf FROM Documente WHERE id_document = @id";
                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@id", idDocument);
                    object rezultat = cmd.ExecuteScalar();

                    if (rezultat != null && rezultat != DBNull.Value)
                    {
                        string caleFisier = rezultat.ToString();
                        if (File.Exists(caleFisier))
                        {
                            Console.WriteLine("Se deschide PDF-ul...");
                            Process.Start(new ProcessStartInfo
                            {
                                FileName = caleFisier,
                                UseShellExecute = true
                            });
                        }
                        else
                        {
                            Console.WriteLine("Fișierul PDF nu a fost găsit la calea salvată.");
                        }
                    }
                    else
                    {
                        Console.WriteLine("Nu există document cu acest ID sau nu are fișier asociat.");
                    }
                }
            }
        }
    }
}







