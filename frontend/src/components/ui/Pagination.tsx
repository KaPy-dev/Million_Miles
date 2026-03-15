'use client';

import styles from './Pagination.module.css';

interface PaginationProps {
    page: number;
    totalPages: number;
    onPageChange: (newPage: number) => void;
}

export default function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
    if (totalPages <= 1) return null;

    return (
        <div className={styles.pagination}>
            <button
                className={styles.button}
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
            >
                Previous
            </button>

            <span className={styles.info}>
                Page {page} of {totalPages}
            </span>

            <button
                className={styles.button}
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
            >
                Next
            </button>
        </div>
    );
}
