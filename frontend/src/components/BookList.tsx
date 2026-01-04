import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button, Table, Alert, Spinner, Modal } from 'react-bootstrap';
import { Book } from '../types';
import { useApi } from '../hooks/useApi';

const POLL_INTERVAL_MS = 2000;

const BookList: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [bookToDelete, setBookToDelete] = useState<Book | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { loading, error, callApi } = useApi<Book[]>();

  const isMountedRef = useRef(true);
  const pollTimerRef = useRef<number | null>(null);

  const fetchBooks = useCallback(async () => {
    const result = await callApi('/api/books');
    if (result && isMountedRef.current) {
      setBooks(result);
    }
    return result;
  }, [callApi]);

  const hasPendingThumbs = useCallback((list: Book[]) => {
    return list.some(b => !!b.image_key && !b.thumb_url);
  }, []);

  useEffect(() => {
    isMountedRef.current = true;

    const start = async () => {
      const first = await fetchBooks();

      if (first && hasPendingThumbs(first)) {
        pollTimerRef.current = window.setInterval(async () => {
          const updated = await fetchBooks();
          if (updated && !hasPendingThumbs(updated)) {
            if (pollTimerRef.current) {
              clearInterval(pollTimerRef.current);
              pollTimerRef.current = null;
            }
          }
        }, POLL_INTERVAL_MS);
      }
    };

    start();

    return () => {
      isMountedRef.current = false;
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [fetchBooks, hasPendingThumbs]);

  const handleDeleteClick = (book: Book) => {
    setBookToDelete(book);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!bookToDelete) return;

    setDeleting(true);
    try {
      const response = await fetch(`/api/books/${bookToDelete.id}`, { method: 'DELETE' });
      if (response.ok) {
        setBooks(prev => prev.filter(book => book.id !== bookToDelete.id));
        setShowDeleteModal(false);
        setBookToDelete(null);
      } else {
        alert('Erro ao excluir o livro');
      }
    } catch {
      alert('Erro ao excluir o livro');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setBookToDelete(null);
  };

  if (loading && books.length === 0) {
    return (
      <div className="d-flex justify-content-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Carregando...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">Erro ao carregar livros: {error}</Alert>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">Lista de Livros</h2>
        <Link to="/books/new">
          <Button variant="success">➕ Novo livro</Button>
        </Link>
      </div>

      <div className="table-responsive">
        <Table striped bordered hover responsive className="align-middle text-center">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Código</th>
              <th>Título</th>
              <th>Autor</th>
              <th>Thumb</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {books.map(book => (
              <tr key={book.id}>
                <td>{book.id}</td>
                <td>{book.code}</td>
                <td>{book.title}</td>
                <td>{book.author}</td>
                <td>
                  {book.thumb_url ? (
                    <img
                      className="thumb"
                      src={book.thumb_url}
                      alt={`thumb ${book.title}`}
                      style={{ height: '60px', borderRadius: '6px' }}
                    />
                  ) : book.image_key ? (
                    <span className="text-muted">Processando…</span>
                  ) : (
                    '—'
                  )}
                </td>
                <td>
                  <Link to={`/books/${book.id}`}>
                    <Button variant="primary" size="sm">Ver</Button>
                  </Link>
                  <Button
                    variant="danger"
                    size="sm"
                    className="ms-1"
                    onClick={() => handleDeleteClick(book)}
                  >
                    Excluir
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <Modal show={showDeleteModal} onHide={handleDeleteCancel} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirmar Exclusão</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Tem certeza que deseja excluir o livro "{bookToDelete?.title}"?
          Esta ação não pode ser desfeita.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleDeleteCancel}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={handleDeleteConfirm} disabled={deleting}>
            {deleting ? <Spinner as="span" animation="border" size="sm" /> : null}
            Excluir
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default BookList;
