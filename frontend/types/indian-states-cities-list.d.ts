// Type definitions for indian-states-cities-list 1.0.5
// Project: https://www.npmjs.com/package/indian-states-cities-list

interface StateItem {
  label: string;
  value: string;
  name: string;
}

interface CityItem {
  label: string;
  value: string;
}

interface IndianStatesCities {
  INDIAN_STATES_AND_UT_ARRAY: string[];
  STATES_OBJECT: StateItem[];
  STATE_WISE_CITIES: Record<string, CityItem[]>;
}

declare module 'indian-states-cities-list' {
  const IndianStatesCities: IndianStatesCities;
  export default IndianStatesCities;
}