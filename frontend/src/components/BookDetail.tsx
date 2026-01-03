import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button, Card, Table, Form, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { Book, Rental } from '../types';
import { useApi } from '../hooks/useApi';

const BookDetail: React.FC = () => {
  const [book, setBook] = useState<Book | null>(null);
  const [renter, setRenter] = useState('');
  const [renting, setRenting] = useState(false);
  const [returning, setReturning] = useState<number | null>(null);
  const { id } = useParams<{ id: string }>();
  const { data, loading, error, callApi } = useApi<Book>();

  const fetchBookDetails = async () => {
    if (id) {
      const result = await callApi(`/api/books/${id}`);
      if (result) {
        setBook(result);
      }
    }
  };

  useEffect(() => {
    fetchBookDetails();
  }, [id, callApi]);

  const handleRent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (id && renter.trim()) {
      setRenting(true);
      try {
        const response = await fetch(`/api/books/${id}/rentals`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ renter: renter.trim() }),
        });
        if (response.ok) {
          await fetchBookDetails();
          setRenter('');
        } else {
          alert('Erro ao alugar o livro');
        }
      } catch (error) {
        alert('Erro ao alugar o livro');
      } finally {
        setRenting(false);
      }
    }
  };

  const handleReturn = async (rentalId: number) => {
    setReturning(rentalId);
    try {
      const response = await fetch(`/api/rentals/${rentalId}/return`, { method: 'PUT' });
      if (response.ok) {
        await fetchBookDetails();
      } else {
        alert('Erro ao devolver o livro');
      }
    } catch (error) {
      alert('Erro ao devolver o livro');
    } finally {
      setReturning(null);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Carregando...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">Erro ao carregar detalhes do livro: {error}</Alert>;
  }

  if (!book) {
    return <Alert variant="info">Livro não encontrado</Alert>;
  }

  return (
    <>
      <Link to="/" className="btn btn-link mb-2">← Voltar</Link>

      <Card className="shadow-sm">
        <Card.Body>
          <div className="d-flex justify-content-between align-items-center">
            <Card.Title as="h2" className="mb-0">{book.title} <small className="text-muted">({book.code})</small></Card.Title>
            <Link to={`/books/${book.id}/edit`}>
              <Button variant="warning">Editar</Button>
            </Link>
          </div>

          <p><strong>Autor:</strong> {book.author}</p>
          <p>{book.summary || ''}</p>

          {book.thumb_url && (
            <Card.Img src={book.thumb_url} className="img-thumbnail mb-3" style={{ maxHeight: '200px', width: 'auto' }} alt={`thumb ${book.title}`} />
          )}
        </Card.Body>
      </Card>

      <h3 className="mt-4">Aluguéis</h3>

      <Form onSubmit={handleRent} className="mb-3">
        <Row className="g-2 align-items-center">
          <Col md={4}>
            <Form.Control type="text" placeholder="Locatário" value={renter} onChange={e => setRenter(e.target.value)} required />
          </Col>
          <Col xs="auto">
            <Button variant="primary" type="submit">Alugar</Button>
          </Col>
        </Row>
      </Form>

      <div className="table-responsive">
        <Table bordered className="align-middle text-center">
          <thead className="table-secondary">
            <tr>
              <th>ID</th><th>Locatário</th><th>Início</th><th>Fim</th><th>Status</th><th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {(book.rentals || []).map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.renter}</td>
                <td>{r.start_date}</td>
                <td>{r.end_date || '—'}</td>
                <td>{r.status}</td>
                <td>
                  {r.status === 'OPEN' && (
                    <Button variant="success" size="sm" onClick={() => handleReturn(r.id)} disabled={returning === r.id}>
                      {returning === r.id ? <Spinner as="span" animation="border" size="sm" /> : 'Devolver'}
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </>
  );
};

export default BookDetail;
