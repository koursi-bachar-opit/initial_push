import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Spinner } from 'flowbite-react';
import { api } from './api/client';
import type { MachineListing } from './types';
import { ListingModal } from './components/ListingModal';
import { FiltersSidebar } from './components/FiltersSidebar';

// Define the onBookingRequest prop type
interface OnBookingRequestProps {
  onBookingRequest: (listing: MachineListing, startTime: string, endTime: string, selectedDate: string, organizationId: string | null) => Promise<void>;
}

export const ListingsApp: React.FC = () => {
  const [listings, setListings] = useState<MachineListing[]>([]);
  const [filteredListings, setFilteredListings] = useState<MachineListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedListing, setSelectedListing] = useState<MachineListing | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'my'>('all');
  const [filters, setFilters] = useState({
    search: '',
    minPrice: '',
    maxPrice: '',
    minCpuCores: '',
    minRamGb: '',
    gpuModel: '',
    minGpuCount: '',
    minVramGb: '',
    minStorageGb: '',
    minNetworkMbps: '',
    locationRegion: '',
    cpuModel: '',
    sortBy: 'created_at',
    sortOrder: 'desc'
  });

  useEffect(() => {
    loadListings();
  }, []);

  const loadListings = async () => {
    try {
      setLoading(true);
      const response = await api.getListings();
      setListings(response.data.data);
      setFilteredListings(response.data.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load listings');
      console.error('Error loading listings:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...listings];

    // Apply search filter
    if (filters.search) {
      filtered = filtered.filter(listing => 
        listing.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        listing.machine.hostname.toLowerCase().includes(filters.search.toLowerCase()) ||
        (listing.description && listing.description.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    // Apply price filters
    if (filters.minPrice) {
      filtered = filtered.filter(listing => listing.hourly_price >= parseFloat(filters.minPrice));
    }
    if (filters.maxPrice) {
      filtered = filtered.filter(listing => listing.hourly_price <= parseFloat(filters.maxPrice));
    }

    // Apply CPU filter
    if (filters.minCpuCores) {
      filtered = filtered.filter(listing => listing.machine.cpu_cores >= parseInt(filters.minCpuCores));
    }

    // Apply RAM filter
    if (filters.minRamGb) {
      filtered = filtered.filter(listing => listing.machine.ram_gb >= parseInt(filters.minRamGb));
    }

    // Apply GPU filters
    if (filters.gpuModel) {
      filtered = filtered.filter(listing => 
        listing.machine.gpu_model.toLowerCase().includes(filters.gpuModel.toLowerCase())
      );
    }
    if (filters.minGpuCount) {
      filtered = filtered.filter(listing => listing.machine.gpu_count >= parseInt(filters.minGpuCount));
    }
    if (filters.minVramGb) {
      filtered = filtered.filter(listing => listing.machine.vram_gb >= parseInt(filters.minVramGb));
    }

    // Apply storage filter
    if (filters.minStorageGb) {
      filtered = filtered.filter(listing => listing.machine.storage_gb >= parseInt(filters.minStorageGb));
    }

    // Apply network filter
    if (filters.minNetworkMbps) {
      filtered = filtered.filter(listing => listing.machine.network_mbps >= parseInt(filters.minNetworkMbps));
    }

    // Apply location filter
    if (filters.locationRegion) {
      filtered = filtered.filter(listing => 
        listing.machine.location_region.toLowerCase().includes(filters.locationRegion.toLowerCase())
      );
    }

    // Apply CPU model filter
    if (filters.cpuModel) {
      filtered = filtered.filter(listing => 
        listing.machine.cpu_model.toLowerCase().includes(filters.cpuModel.toLowerCase())
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (filters.sortBy) {
        case 'price':
          aValue = a.hourly_price;
          bValue = b.hourly_price;
          break;
        case 'cpu_cores':
          aValue = a.machine.cpu_cores;
          bValue = b.machine.cpu_cores;
          break;
        case 'ram_gb':
          aValue = a.machine.ram_gb;
          bValue = b.machine.ram_gb;
          break;
        case 'storage_gb':
          aValue = a.machine.storage_gb;
          bValue = b.machine.storage_gb;
          break;
        default:
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
      }

      if (filters.sortOrder === 'asc') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    });

    setFilteredListings(filtered);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      minPrice: '',
      maxPrice: '',
      minCpuCores: '',
      minRamGb: '',
      gpuModel: '',
      minGpuCount: '',
      minVramGb: '',
      minStorageGb: '',
      minNetworkMbps: '',
      locationRegion: '',
      cpuModel: '',
      sortBy: 'created_at',
      sortOrder: 'desc'
    });
    setFilteredListings(listings);
  };

  const openListingModal = (listing: MachineListing) => {
    setSelectedListing(listing);
    setShowModal(true);
  };

  const handleBookingRequest = async (listing: MachineListing, startTime: string, endTime: string, selectedDate: string, organizationId: string | null) => {
    try {
      // Implement booking logic here
      const startDateTime = new Date(`${selectedDate}T${startTime}`);
      const endDateTime = new Date(`${selectedDate}T${endTime}`);

      const payload = {
        listing_id: listing.id,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        organization_id: organizationId
      };

      // Call your booking API
      const response = await api.requestBooking(payload);
      alert('Booking requested successfully!');
      setShowModal(false);
    } catch (error: any) {
      alert(`Booking failed: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <Spinner size="xl" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading listings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full mb-4">
          <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Error Loading Listings</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
        <Button color="light" onClick={loadListings}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Server Listings</h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">Find the perfect compute power for your needs</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          <div className="lg:w-1/4">
            <FiltersSidebar
              filters={filters}
              setFilters={setFilters}
              applyFilters={applyFilters}
              clearFilters={clearFilters}
              resultsCount={filteredListings.length}
            />
          </div>

          {/* Results Area */}
          <div className="lg:w-3/4">
            {/* Tabs */}
            <div className="mb-6">
              <div className="border-b border-gray-200 dark:border-gray-700">
                <div className="flex space-x-2">
                  <button
                    className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${activeTab === 'all' 
                      ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-500' 
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
                    onClick={() => setActiveTab('all')}
                  >
                    All Listings ({listings.length})
                  </button>
                  <button
                    className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${activeTab === 'my' 
                      ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-500' 
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
                    onClick={() => setActiveTab('my')}
                  >
                    My Listings
                  </button>
                </div>
              </div>
            </div>

            {/* Results Info */}
            {filteredListings.length > 0 && (
              <div className="mb-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-blue-800 dark:text-blue-300 font-medium">
                      {filteredListings.length}
                    </span>
                    <span className="text-blue-600 dark:text-blue-400 ml-1">
                      {filteredListings.length === 1 ? 'result' : 'results'} found
                    </span>
                  </div>
                  <button
                    onClick={clearFilters}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Clear filters
                  </button>
                </div>
              </div>
            )}

            {/* Listings Grid */}
            {filteredListings.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No listings found</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Try adjusting your filters or search term</p>
                <Button color="light" onClick={clearFilters}>Clear Filters</Button>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredListings.map((listing) => (
                  <ListingCard
                    key={listing.id}
                    listing={listing}
                    onClick={() => openListingModal(listing)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Custom Modal Implementation */}
        {showModal && selectedListing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <ListingModal
            listing={selectedListing}
            show={showModal} // Add this
            onClose={() => setShowModal(false)}
            onBookingRequest={handleBookingRequest}
            />
        </div>
        )}
      </div>
    </div>
  );
};

// Listing Card Component
const ListingCard: React.FC<{ listing: MachineListing; onClick: () => void }> = ({ listing, onClick }) => {
  return (
    <Card 
      className="hover:shadow-xl transition-shadow duration-300 cursor-pointer transform hover:-translate-y-1"
      onClick={onClick}
    >
      <div className="relative">
        {/* Price Badge */}
        <div className="absolute top-2 right-2 z-10">
          <Badge color="blue" className="font-semibold">
            ${listing.hourly_price}/hr
          </Badge>
        </div>

        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 line-clamp-1">
          {listing.title}
        </h3>
        
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
          {listing.description || listing.machine.notes || 'High-performance compute server'}
        </p>

        {/* Quick Specs */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">CPU:</span>
            <span className="text-gray-900 dark:text-white">{listing.machine.cpu_cores} cores</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 5a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm11 1H6v8l4-2 4 2V6z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">RAM:</span>
            <span className="text-gray-900 dark:text-white">{listing.machine.ram_gb} GB</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">GPU:</span>
            <span className="text-gray-900 dark:text-white">{listing.machine.gpu_model} ×{listing.machine.gpu_count}</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Region:</span>
            <span className="text-gray-900 dark:text-white">{listing.machine.location_region}</span>
          </div>
        </div>

        {/* Action Button */}
        <Button
          fullSized
          color="blue"
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          className="mt-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
        >
          <div className="flex items-center justify-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            View Details & Book
          </div>
        </Button>
      </div>
    </Card>
  );
};