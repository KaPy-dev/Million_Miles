'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import Navbar from '@/components/ui/Navbar';
import CarCard from '@/components/ui/CarCard';
import Pagination from '@/components/ui/Pagination';
import { fetchApi } from '@/lib/api';
import styles from './page.module.css';

interface FilterState {
  maker: string;
  model: string;
  price_min: string;  
  price_max: string;  
  search: string;
}

export default function Home() {
  const [cars, setCars] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [filters, setFilters] = useState<FilterState>({
    maker: '',
    model: '',
    price_min: '',  
    price_max: '', 
    search: ''
  });

  const [sortBy, setSortBy] = useState('-scraped_at');
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const loadCars = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('limit', '15');
      params.append('sort_by', sortBy);

      // Добавляем фильтры
      if (filters.maker.trim()) params.append('maker', filters.maker.trim());
      if (filters.model.trim()) params.append('model', filters.model.trim());
      
      // Цены — проверяем что это число и больше 0
      const minPrice = parseInt(filters.price_min);
      if (!isNaN(minPrice) && minPrice > 0) {
        params.append('price_min', minPrice.toString());
      }
      
      const maxPrice = parseInt(filters.price_max);
      if (!isNaN(maxPrice) && maxPrice > 0) {
        params.append('price_max', maxPrice.toString());
      }
      
      // Поиск
      if (filters.search.trim()) {
        params.append('search', filters.search.trim());
      }

      console.log('Fetching with params:', params.toString());

      const data = await fetchApi(`/cars?${params.toString()}`);
      
      setCars(data.items || []);
      setTotalItems(data.total || 0);
      setTotalPages(Math.ceil((data.total || 0) / 12));
      
    } catch (err: any) {
      console.error('Failed to load cars:', err);
      setError(err.message || 'Failed to load cars');
    } finally {
      setIsLoading(false);
    }
  }, [page, filters, sortBy]);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      loadCars();
    }, 400);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [loadCars]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(1);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value }));
    setPage(1);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortBy(e.target.value);
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      maker: '',
      model: '',
      price_min: '',
      price_max: '',
      search: ''
    });
    setPage(1);
  };

  const hasActiveFilters = filters.maker || filters.model || filters.price_min || filters.price_max || filters.search;

  return (
    <div className={styles.main}>
      <Navbar />

      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Find Your <span className={styles.highlight}>Dream Car</span></h1>
          <p className={styles.subtitle}>Explore our curated collection of premium vehicles directly from Japan.</p>
        </div>

        
        <div className={styles.searchBar}>
          <input
            type="text"
            placeholder="Search by maker, model, or keywords..."
            className={styles.searchInput}
            value={filters.search}
            onChange={handleSearchChange}
          />
          {filters.search && (
            <button 
              className={styles.clearSearch} 
              onClick={() => setFilters(prev => ({ ...prev, search: '' }))}
              type="button"
            >
              ×
            </button>
          )}
        </div>

        <div className={styles.contentAndSidebar}>
          <aside className={styles.sidebar}>
            <div className={styles.filterBox}>
              <div className={styles.filterHeader}>
                <h2 className={styles.filterTitle}>Search Filters</h2>
                {hasActiveFilters && (
                  <button onClick={clearFilters} className={styles.clearBtn} type="button">
                    Clear All
                  </button>
                )}
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.label} htmlFor="maker">Maker</label>
                <input
                  id="maker"
                  name="maker"
                  type="text"
                  placeholder="e.g. Toyota"
                  className={styles.input}
                  value={filters.maker}
                  onChange={handleFilterChange}
                />
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.label} htmlFor="model">Model</label>
                <input
                  id="model"
                  name="model"
                  type="text"
                  placeholder="e.g. Prius"
                  className={styles.input}
                  value={filters.model}
                  onChange={handleFilterChange}
                />
              </div>

              <div className={styles.filterRow}>
                <div className={styles.filterGroup}>
                  <label className={styles.label} htmlFor="price_min">Min Price (¥)</label>
                  <input
                    id="price_min"
                    name="price_min" 
                    type="number"
                    min="0"
                    placeholder="0"
                    className={styles.input}
                    value={filters.price_min}
                    onChange={handleFilterChange}
                  />
                </div>

                <div className={styles.filterGroup}>
                  <label className={styles.label} htmlFor="price_max">Max Price (¥)</label>
                  <input
                    id="price_max"
                    name="price_max" 
                    type="number"
                    min="0"
                    placeholder="∞"
                    className={styles.input}
                    value={filters.price_max}
                    onChange={handleFilterChange}
                  />
                </div>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.label} htmlFor="sortBy">Sort By</label>
                <select 
                  id="sortBy"
                  className={styles.select} 
                  value={sortBy} 
                  onChange={handleSortChange}
                >
                  <option value="-scraped_at">Newest First</option>
                  <option value="price">Price: Low to High</option>
                  <option value="-price">Price: High to Low</option>
                  <option value="-year">Year: Newest First</option>
                  <option value="year">Year: Oldest First</option>
                  <option value="mileage">Mileage: Lowest First</option>
                  <option value="-mileage">Mileage: Highest First</option>
                </select>
              </div>

              {isLoading && <div className={styles.loadingIndicator}>Loading...</div>}
            </div>
          </aside>

          <main className={styles.dashboard}>
            <div className={styles.resultsHeader}>
              <span className={styles.resultsCount}>
                {isLoading ? 'Loading...' : `Showing ${cars.length} of ${totalItems} matches`}
              </span>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            {!isLoading && cars.length === 0 ? (
              <div className={styles.noResults}>
                <h3>No cars found</h3>
                <p>Try adjusting your filters</p>
                {hasActiveFilters && (
                  <button onClick={clearFilters} className={styles.clearBtnLarge}>
                    Clear All Filters
                  </button>
                )}
              </div>
            ) : (
              <>
                <div className={styles.grid}>
                  {cars.map(car => (
                    <CarCard key={car.id} car={car} />
                  ))}
                </div>

                {totalPages > 1 && (
                  <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}