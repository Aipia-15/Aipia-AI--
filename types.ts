
export type Language = 'ja' | 'en' | 'ko' | 'es' | 'de' | 'fr';
export type WalkingSpeed = 'slow' | 'normal' | 'fast';

export interface UserPreferences {
  adults: number;
  children: number;
  genre: string;
  prefecture: string;
  budget: number;
  departure: string;
  startDate: string;
  endDate: string;
  keywords: string;
  language: Language;
  walkingSpeed: WalkingSpeed;
  accommodationType?: string;
  transportPreference?: string;
}

export interface GroundingLink {
  title: string;
  uri: string;
}

export interface TimelineItem {
  id: string;
  time: string;
  action: string;
  description: string;
  transport?: string;
  transitDetail?: string;
  departureStation?: string;
  arrivalStation?: string;
  cost: number;
  officialUrl?: string;
  isAiRecommended?: boolean;
  nearbyFood?: string;
  nearbyLandmark?: string;
  nearbySecret?: string;
  // Added line property to support transport line information from AI generated plans
  line?: string;
}

export interface DayPlan {
  dayNumber: number;
  activities: TimelineItem[];
}

export interface NearbySpot {
  name: string;
  address: string;
  description: string;
  type: 'spot' | 'food';
}

export interface AccommodationOption {
  id: string;
  name: string;
  description: string;
  estimatedCost: number;
  officialUrl: string;
  imageUrl: string;
  type: string;
}

export interface TravelPlan {
  id: string;
  theme: string;
  days: DayPlan[];
  selectedAccommodationId?: string;
  accommodations: AccommodationOption[];
  budgetBreakdown: {
    transport: number;
    accommodation: number;
    activity: number;
    food: number;
  };
  nearbySpots: NearbySpot[];
  proTips: string[];
  groundingSources: GroundingLink[];
  createdAt: string;
  durationDays: number;
  dateRange: {
    start: string;
    end: string;
  };
  totalCost?: number;
  imageKeyword?: string;
}

export interface FavoriteItem {
  id: string;
  plan: TravelPlan;
  isFinalized?: boolean;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  prefecture: string;
  genre: string;
  imageUrl: string;
  groundingSources?: GroundingLink[];
}
