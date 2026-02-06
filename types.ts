
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
}

export interface GroundingLink {
  title: string;
  uri: string;
}

export interface TimelineItem {
  time: string;
  action: string;
  description: string;
  transport?: string;
  departureStation?: string;
  arrivalStation?: string;
  departureTime?: string;
  arrivalTime?: string;
  detailedCost?: string;
  officialUrl?: string;
}

export interface DayPlan {
  dayNumber: number;
  activities: TimelineItem[];
}

export interface NearbySpot {
  name: string;
  address: string;
  type: 'spot' | 'food';
}

export interface TravelPlan {
  id: string;
  theme: string;
  days: DayPlan[];
  accommodation: {
    name: string;
    description: string;
    estimatedCost: string;
    officialUrl?: string;
  };
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
}

export interface FavoriteItem {
  id: string;
  plan: TravelPlan;
  isFinalized?: boolean;
  detailedPlan?: TravelPlan;
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