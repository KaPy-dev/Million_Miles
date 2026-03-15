'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import styles from './page.module.css';

interface CarDetail {
id: string;
source_id: string;
source_url: string;
maker: string;
model: string;
grade: string;
year: number;
mileage_km: number;
price_jpy: number;
total_price_jpy: number;
color: string;
fuel_type: string;
transmission: string;
body_type: string;
displacement_cc: number;
drive: string;
doors: number;
seats: number;
condition_score: number;
has_accident: boolean;
location: string;
shop_name: string;
images: string[];
equipment: Record<string, string[]>;
scraped_at: string;
}

export default function CarDetailPage() {
const params = useParams();
const router = useRouter();
const [car, setCar] = useState<CarDetail | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState('');
const [selectedImage, setSelectedImage] = useState(0);

useEffect(() => {
    const loadCar = async () => {
    try {
        const data = await fetchApi(`/cars/${params.id}`);
        setCar(data);
    } catch (err: any) {
        setError(err.message || 'Failed to load car details');
    } finally {
        setLoading(false);
    }
    };

    if (params.id) {
    loadCar();
    }
}, [params.id]);

const formatPrice = (price?: number) => {
    if (!price) return 'Contact for price';
    return `¥${price.toLocaleString()}`;
};

const formatMileage = (km?: number) => {
    if (!km) return 'N/A';
    if (km >= 10000) {
    return `${(km / 10000).toFixed(1)}万 km`;
    }
    return `${km.toLocaleString()} km`;
};

const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
    });
};

if (loading) {
    return (
    <div className={styles.main}>
        <div className={styles.container}>
        <div className={styles.loaderContainer}>
            <div className={styles.loader}></div>
        </div>
        </div>
    </div>
    );
}

if (error || !car) {
    return (
    <div className={styles.main}>
        <div className={styles.container}>
        <div className={styles.error}>
            <h2>Error</h2>
            <p>{error || 'Car not found'}</p>
            <button onClick={() => router.push('/')} className={styles.backBtn}>
            ← Back to Search
            </button>
        </div>
        </div>
    </div>
    );
}

const mainImage = car.images?.[selectedImage] || null;

return (
    <div className={styles.main}>
    <div className={styles.container}>
        <button onClick={() => router.push('/')} className={styles.backBtn}>
        ← Back to Search
        </button>


        <div className={styles.heroSection}>

        <div className={styles.imageGallery}>
            <div className={styles.mainImageWrapper}>
            {mainImage ? (
                <img 
                src={mainImage} 
                alt={`${car.maker} ${car.model}`}
                className={styles.mainImage}
                />
            ) : (
                <div className={styles.noImage}>No Image Available</div>
            )}
            </div>
            
            {car.images && car.images.length > 1 && (
            <div className={styles.thumbnails}>
                {car.images.map((img, idx) => (
                <div 
                    key={idx}
                    className={`${styles.thumbWrapper} ${selectedImage === idx ? styles.activeThumb : ''}`}
                    onClick={() => setSelectedImage(idx)}
                >
                    <img src={img} alt="" className={styles.thumbnail} />
                </div>
                ))}
            </div>
            )}
        </div>


        <div className={styles.keyInfo}>
            <div className={styles.titleBadge}>
            <h1 className={styles.title}>{car.maker} {car.model}</h1>
            {car.grade && <span className={styles.grade}>{car.grade}</span>}
            </div>

            <div className={styles.priceContainer}>
            <div className={styles.mainPrice}>{formatPrice(car.price_jpy)}</div>
            {car.total_price_jpy && car.total_price_jpy !== car.price_jpy && (
                <div className={styles.totalPrice}>
                Total Price: <span>{formatPrice(car.total_price_jpy)}</span>
                </div>
            )}
            </div>

            <div className={styles.specsGrid}>
            <div className={styles.specBox}>
                <span className={styles.specLabel}>Year</span>
                <span className={styles.specValue}>{car.year || 'N/A'}</span>
            </div>
            <div className={styles.specBox}>
                <span className={styles.specLabel}>Mileage</span>
                <span className={styles.specValue}>{formatMileage(car.mileage_km)}</span>
            </div>
            <div className={styles.specBox}>
                <span className={styles.specLabel}>Color</span>
                <span className={styles.specValue}>{car.color || 'N/A'}</span>
            </div>
            <div className={styles.specBox}>
                <span className={styles.specLabel}>Fuel Type</span>
                <span className={styles.specValue}>{car.fuel_type || 'N/A'}</span>
            </div>
            </div>

            <div className={styles.actionSection}>
            <a 
                href={car.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className={styles.primaryAction}
            >
                View on CarSensor
            </a>
            </div>
        </div>
        </div>

        <div className={styles.detailsSection}>
        <h2 className={styles.sectionTitle}>Full Specifications</h2>
        <div className={styles.detailsGrid}>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Maker</span>
            <span className={styles.dv}>{car.maker || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Model</span>
            <span className={styles.dv}>{car.model || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Grade</span>
            <span className={styles.dv}>{car.grade || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Year</span>
            <span className={styles.dv}>{car.year || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Mileage</span>
            <span className={styles.dv}>{formatMileage(car.mileage_km)}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Price</span>
            <span className={styles.dv}>{formatPrice(car.price_jpy)}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Total Price</span>
            <span className={styles.dv}>{formatPrice(car.total_price_jpy)}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Color</span>
            <span className={styles.dv}>{car.color || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Fuel Type</span>
            <span className={styles.dv}>{car.fuel_type || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Transmission</span>
            <span className={styles.dv}>{car.transmission || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Body Type</span>
            <span className={styles.dv}>{car.body_type || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Engine Displacement</span>
            <span className={styles.dv}>{car.displacement_cc ? `${car.displacement_cc} cc` : 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Drive Type</span>
            <span className={styles.dv}>{car.drive || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Doors</span>
            <span className={styles.dv}>{car.doors || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Seats</span>
            <span className={styles.dv}>{car.seats || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Condition Score</span>
            <span className={styles.dv}>{car.condition_score || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Accident History</span>
            <span className={styles.dv}>
                {car.has_accident === true ? 'Yes' : 
                car.has_accident === false ? 'No' : 'Unknown'}
            </span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Location</span>
            <span className={styles.dv}>{car.location || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Shop Name</span>
            <span className={styles.dv}>{car.shop_name || 'N/A'}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Source ID</span>
            <span className={styles.dv}>{car.source_id}</span>
            </div>
            <div className={styles.detailRow}>
            <span className={styles.dl}>Last Updated</span>
            <span className={styles.dv}>{formatDate(car.scraped_at)}</span>
            </div>
        </div>
        </div>

        {car.equipment && Object.keys(car.equipment).length > 0 && (
        <div className={styles.equipmentSection}>
            <h2 className={styles.sectionTitle}>Equipment & Features</h2>
            {Object.entries(car.equipment).map(([category, items]) => (
            <div key={category} className={styles.equipCategory}>
                <h3 className={styles.equipCategoryTitle}>{category}</h3>
                <div className={styles.equipmentTags}>
                {items.map((item, idx) => (
                    <span key={idx} className={styles.equipTag}>{item}</span>
                ))}
                </div>
            </div>
            ))}
        </div>
        )}
    </div>
    </div>
);
}