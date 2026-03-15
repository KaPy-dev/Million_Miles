export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    if (options.body instanceof FormData) {
        headers.delete('Content-Type');
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        if (response.status === 401 && typeof window !== 'undefined') {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API request failed');
    }

    return response.json();
};
