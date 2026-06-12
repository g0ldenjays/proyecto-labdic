from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.inventory import Book, LoanRequestBookItem

engine = create_engine(settings.database_url.unicode_string())


BOOKS = [
    {
        "title": "The Art of Computer Programming",
        "author": "Donald Knuth",
        "isbn": "9780201896831",
        "topic": "Algoritmos",
        "description": "Obra clásica sobre algoritmos, análisis matemático y estructuras de datos.",
    },
    {
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen",
        "isbn": "9780262046305",
        "topic": "Algoritmos",
        "description": "Texto de referencia para diseño y análisis de algoritmos.",
    },
    {
        "title": "Computer Networking: A Top-Down Approach",
        "author": "James F. Kurose",
        "isbn": "9780136681557",
        "topic": "Redes",
        "description": "Introducción moderna a redes de computadores desde aplicaciones hasta capa física.",
    },
    {
        "title": "Operating System Concepts",
        "author": "Abraham Silberschatz",
        "isbn": "9781119800361",
        "topic": "Sistemas Operativos",
        "description": "Fundamentos de sistemas operativos, procesos, memoria, archivos y concurrencia.",
    },
    {
        "title": "Database System Concepts",
        "author": "Abraham Silberschatz",
        "isbn": "9780078022159",
        "topic": "Bases de Datos",
        "description": "Conceptos centrales de bases de datos relacionales, SQL, diseño y transacciones.",
    },
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "topic": "Programación",
        "description": "Buenas prácticas para escribir código legible, mantenible y profesional.",
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "9780201633610",
        "topic": "Ingeniería de Software",
        "description": "Catálogo clásico de patrones de diseño orientados a objetos.",
    },
    {
        "title": "Computer Organization and Design",
        "author": "David A. Patterson, John L. Hennessy",
        "isbn": "9780128201091",
        "topic": "Arquitectura de Computadores",
        "description": "Fundamentos de arquitectura de computadores, procesadores, memoria e instrucciones.",
    },
    {
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell, Peter Norvig",
        "isbn": "9780134610993",
        "topic": "Inteligencia Artificial",
        "description": "Texto amplio sobre agentes inteligentes, búsqueda, aprendizaje y razonamiento.",
    },
    {
        "title": "Software Engineering",
        "author": "Ian Sommerville",
        "isbn": "9780137035151",
        "topic": "Ingeniería de Software",
        "description": "Introducción a procesos, requisitos, diseño, pruebas y gestión de software.",
    },
]


def run() -> None:
    print("\nIniciando seed de libros...\n")

    with Session(engine) as session:
        try:
            session.query(LoanRequestBookItem).delete()
            session.query(Book).delete()
            session.flush()

            books = [
                Book(
                    title=item["title"],
                    author=item["author"],
                    isbn=item["isbn"],
                    topic=item["topic"],
                    description=item["description"],
                    total_quantity=4,
                    available_quantity=4,
                    is_active=True,
                )
                for item in BOOKS
            ]

            session.add_all(books)
            session.commit()

            print("Libros reiniciados correctamente.")
            print(f"   Total insertado: {len(books)} libros")
            print("   Stock por libro: 4\n")

        except Exception as e:
            session.rollback()
            print(f"Error durante seedbooks, rollback ejecutado: {e}")
            raise


if __name__ == "__main__":
    run()