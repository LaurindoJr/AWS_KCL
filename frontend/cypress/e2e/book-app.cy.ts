/// <reference types="cypress" />

describe('Book App E2E Tests', () => {
  beforeEach(() => {
    // Visit the app
    cy.visit('http://localhost:8080');
  });

  it('should load the book list page', () => {
    // Check if the page loads
    cy.contains('Book List').should('be.visible');
  });

  it('should navigate to create book form', () => {
    // Click on a link to create new book (assuming there's a button or link)
    cy.contains('Add Book').click();
    cy.url().should('include', '/books/new');
  });

  it('should create a new book', () => {
    // Navigate to create form
    cy.contains('Add Book').click();

    // Fill out the form (assuming form fields exist)
    cy.get('input[name="title"]').type('Test Book');
    cy.get('input[name="author"]').type('Test Author');

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Check if redirected back to list and book is there
    cy.url().should('eq', 'http://localhost:3000/');
    cy.contains('Test Book').should('be.visible');
  });
});
