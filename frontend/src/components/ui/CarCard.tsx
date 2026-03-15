'use client';

import Link from 'next/link';
import styles from './CarCard.module.css';

interface CarCardProps {
car: {
    id: string;
    maker: string;
    model: string;
    grade?: string;
    year?: number;
    mileage_km?: number;
    price_jpy?: number;
    color?: string;
    image_url?: string;
    images?: string[];
};
}

export default function CarCard({ car }: CarCardProps) {
const imageUrl = car.image_url || (car.images && car.images[0]) || null;

const formatPrice = (price?: number) => {
    if (!price) return 'Contact';
    return `¥${price.toLocaleString()}`;
};

const formatMileage = (km?: number) => {
    if (!km) return 'N/A';
    if (km >= 10000) {
    return `${(km / 10000).toFixed(1)}万 km`;
    }
    return `${km.toLocaleString()} km`;
};

return (
    <Link href={`/car/${car.id}`} className={styles.cardLink}>
    <article className={styles.card}>
        <div className={styles.imageContainer}>
        {imageUrl ? (
            <img 
            src={imageUrl} 
            alt={`${car.maker} ${car.model}`}
            className={styles.image}
            loading="lazy"
            onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
            }}
            />
        ) : null}
        <div className={styles.noImageFallback}>No Image</div>
        <div className={styles.priceTag}>{formatPrice(car.price_jpy)}</div>
        </div>

        <div className={styles.content}>
        <div className={styles.header}>
            <h3 className={styles.title}>
            {car.maker} {car.model}
            {car.grade && <span className={styles.grade}> {car.grade}</span>}
            </h3>
            <span className={styles.yearBadge}>{car.year || 'N/A'}</span>
        </div>

        <div className={styles.details}>
            <div className={styles.detailItem}>
            <span className={styles.detailLabel}>Mileage</span>
            <span className={styles.detailValue}>{formatMileage(car.mileage_km)}</span>
            </div>
            <div className={styles.detailItem}>
            <span className={styles.detailLabel}>Color</span>
            <span className={styles.detailValue}>{car.color || 'N/A'}</span>
            </div>
        </div>

        <div className={styles.footer}>
            <span className={styles.viewDetails}>View Details →</span>
        </div>
        </div>
    </article>
    </Link>
);
}