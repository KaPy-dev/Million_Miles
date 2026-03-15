'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import styles from './Navbar.module.css';

export default function Navbar() {
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        setIsAuthenticated(!!token);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        router.push('/login');
    };

    return (
        <nav className={styles.navbar}>
            <div className={styles.container}>
                <Link href="/" className={styles.brand}>
                    <span className={styles.highlight}>Million</span> Miles
                </Link>
                <div className={styles.actions}>
                    {isAuthenticated ? (
                        <button onClick={handleLogout} className={styles.logoutBtn}>
                            Logout
                        </button>
                    ) : (
                        <Link href="/login" className={styles.loginBtn}>
                            Login
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}
