import { useEffect, useState } from 'react'

/**
 * Custom hook to debounce a value
 * Useful for debouncing input values before making API calls
 * 
 * @param value - The value to debounce
 * @param delay - The number of milliseconds to delay
 * @returns The debounced value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

