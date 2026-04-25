import { createContext, useState } from "react";

interface NavigationContextValue {
  kelasId: string;
  setKelasId: (id: string) => void;
}

export const NavigationContext = createContext<NavigationContextValue>({
  kelasId: "",
  setKelasId: () => {},
});

export function NavigationProvider({ children }: { children: React.ReactNode }) {
  const [kelasId, setKelasId] = useState("");
  return (
    <NavigationContext.Provider value={{ kelasId, setKelasId }}>
      {children}
    </NavigationContext.Provider>
  );
}