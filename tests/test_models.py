# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        # Set the ID of the product object to None and then call the create() method on the product.
        product.create()
        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)
        # Fetch the product back from the system using the product ID and store it in found_product
        found_product = Product.find(product.id)
        # Assert that the properties of the found_product match with the properties of the original product object,
        # such as id, name, description and price.
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        # Set the ID of the product object to None and then call the create() method on the product.
        product.create()
        # Log the product object again after it has been created to verify that the
        # product was created with the desired properties.
        original_id = product.id
        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)
        product.description = "Test Description"
        # Update the product in the system with the new property values using the update() method.
        product.update()
        # Assert that the id is same as the original id but description property of the product
        # object has been updated correctly after calling the update() method.
        self.assertEqual(original_id, product.id)
        self.assertEqual("Test Description", product.description)
        # Fetch all the product back from the system.
        products = Product.all()
        # Assert the length of the products list is equal to 1 to verify that after updating the product,
        # there is only one product in the system.
        self.assertEqual(len(products), 1)
        # Assert that the fetched product has id same as the original id.
        self.assertEqual(products[0].id, original_id)
        # Assert that the fetched product has the updated description.
        self.assertEqual(products[0].description, "Test Description")

    def test_update_product_without_id(self):
        """Raise DataValidationError when updating a product with empty ID"""
        product = ProductFactory()
        product.id = None  # Set ID to None
        with self.assertRaises(DataValidationError) as context:
            product.update()
        self.assertEqual(str(context.exception), "Update called with empty ID field")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        # Call the create() method on the product to save it to the database.
        product.create()
        # Assert  if the length of the list returned by Product.all() is equal to 1,
        # to verify that after creating a product and saving it to the database,
        # there is only one product in the system.
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Call the delete() method on the product object, to remove the product from the database.
        product.delete()
        # Assert if the length of the list returned by Product.all() is now equal to 0,
        # indicating that the product has been successfully deleted from the database.
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_product(self):
        """It should list all the Product"""
        products = Product.all()
        # Assert if the products list is empty, indicating that there are no products
        # in the database at the beginning of the test case.
        self.assertEqual(len(products), 0)
        # Use for loop to create five Product objects using a ProductFactory() and
        # call the create() method on each product to save them to the database.
        for _ in range(5):
            product = ProductFactory()
            # Fetch all products from the database again using product.all()
            product.create()
        products = Product.all()
        # Assert if the length of the products list is equal to 5, to verify that the five products
        # created in the previous step have been successfully added to the database.
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should  find a Product by name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_a_product_by_availability(self):
        """It should  find a Product by availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_a_product_by_category(self):
        """It should  find a Product by category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_a_product_by_price(self):
        """It should find a Product by price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_deserialize_invalid_data(self):
        """It should raise a DataValidationError when the product data is malformed or incomplete"""

        # Create malformed data where price is valid (decimal) but 'available' is an invalid type
        invalid_data = {
            "name": "Test Product",
            "description": "This is a test product",
            "price": 12.50,  # Valid decimal type for price
            "available": "maybe",  # Invalid type for available (should be boolean)
            "category": "CLOTHS"
        }
        # Try to deserialize and catch the exception
        with self.assertRaises(DataValidationError) as context:
            product = Product()
            product.deserialize(invalid_data)
        # Check if the exception message matches the expected one
        self.assertEqual(
            str(context.exception),
            "Invalid type for boolean [available]: <class 'str'>"
        )
