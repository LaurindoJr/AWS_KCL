import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button, Card, Form, Alert, Spinner } from 'react-bootstrap';
import { Book, BookFormData } from '../types';
import { useApi } from '../hooks/useApi';

const BookForm: React.FC = () => {
  const [formData, setFormData] = useState<BookFormData>({
    code: '',
    title: '',
    author: '',
    summary: '',
  });
  const [image, setImage] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);
  const { data: bookData, loading, error, callApi } = useApi<Book>();

  useEffect(() => {
    if (isEditing && id) {
      callApi(`/api/books/${id}`);
    }
  }, [id, isEditing, callApi]);

  useEffect(() => {
    if (bookData && isEditing) {
      setFormData({
        code: bookData.code,
        title: bookData.title,
        author: bookData.author,
        summary: bookData.summary || '',
      });
    }
  }, [bookData, isEditing]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setImage(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);

    const submissionData = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== undefined) {
        submissionData.append(key, value);
      }
    });
    if (image) {
      submissionData.append('image', image);
    }

    try {
      const url = isEditing ? `/api/books/${id}` : '/api/books';
      const method = isEditing ? 'PUT' : 'POST';
      const response = await fetch(url, { method, body: submissionData });

      if (response.ok) {
        navigate(isEditing ? `/books/${id}` : '/');
      } else {
        setSubmitError('Erro ao salvar o livro');
      }
    } catch (error) {
      setSubmitError('Erro ao salvar o livro');
    } finally {
      setSubmitting(false);
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
    return <Alert variant="danger">Erro ao carregar dados do livro: {error}</Alert>;
  }

  return (
    <>
      <Link to="/" className="btn btn-link">← Voltar</Link>

      <Card className="shadow-sm mt-3">
        <Card.Body>
          <Card.Title as="h3">{isEditing ? 'Editar livro' : 'Novo Livro'}</Card.Title>

          {submitError && <Alert variant="danger">{submitError}</Alert>}

          <Form onSubmit={handleSubmit}>
            {!isEditing && (
              <Form.Group className="mb-3">
                <Form.Label>Código</Form.Label>
                <Form.Control type="text" name="code" value={formData.code} onChange={handleChange} required />
              </Form.Group>
            )}

            <Form.Group className="mb-3">
              <Form.Label>Título</Form.Label>
              <Form.Control type="text" name="title" value={formData.title} onChange={handleChange} required />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Autor</Form.Label>
              <Form.Control type="text" name="author" value={formData.author} onChange={handleChange} required />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Resumo</Form.Label>
              <Form.Control as="textarea" name="summary" value={formData.summary} onChange={handleChange} />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Imagem</Form.Label>
              <Form.Control type="file" name="image" accept="image/*" onChange={handleImageChange} />
            </Form.Group>

            <Button variant="primary" type="submit" disabled={submitting}>
              {submitting ? <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> : null}
              Salvar
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </>
  );
};

export default BookForm;
