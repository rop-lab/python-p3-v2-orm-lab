from __init__ import CURSOR, CONN
from department import Department
from employee import Employee



class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self._year = None  # Initialize _year attribute
        self._summary = None
        self._employee_id = None
        self.year = year  # Use property setter to set year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise  ValueError("Year must be an integer greater than  or equal to 2000.")

    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._summary = value
        else:
            raise ValueError("Summary should be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if isinstance(value, int) and Employee.find_by_id(value): 
            self._employee_id = value
        else:
            raise ValueError("Employee_id should be the id of an existing Employee instance.")


    def save(self):
        """Insert a new row into the 'reviews' table and update object attributes."""
        print("Employee ID:", self.employee_id)
        if not Employee.find_by_id(self.employee_id):
            raise ValueError("Employee with provided ID does not exist in the database.")

        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        # Update the object's id attribute with the primary key value of the new row
        self.id = CURSOR.lastrowid

        # Save the object in the local dictionary with the table row's primary key as the dictionary key
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance, save it to the database, and return the new instance."""
        review = cls(year, summary, employee_id)
        review.save()  # Assuming save method persists the Review instance to the database
        return review
    
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        review_id, year, summary, employee_id = row
        review = cls.all.get(review_id)  # If this review has already been instantiated, use it instead of creating

        if review:
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to the row in the 'reviews' table with the given id."""
        sql = """
            SELECT * FROM reviews 
            WHERE id = ?
        """
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()

        if row:
            return cls.instance_from_db(row)
        else:
            return None
        
    def update(self):
        """ Update the 'reviews' table row based on the id of the current object."""
        if self.id is None:
            raise ValueError("Cannot update review; no id set.")
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the 'reviews' table row based on the id of the current object."""
        if self.id is None:
            raise ValueError("Cannot delete object without id")
        sql = """
            DELETE FROM reviews
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list of Review instances for every row in the 'reviews' table."""
        sql = """
            SELECT * FROM reviews
        """
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()

        reviews = []
        for row in rows:
            review = cls.instance_from_db(row)
            reviews.append(review)

        return reviews
    
    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = """
            DROP TABLE IF EXISTS reviews
        """
        CURSOR.execute(sql)
        CONN.commit()

    
   