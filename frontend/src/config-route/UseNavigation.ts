import { useContext } from "react";
import { NavigationContext } from "./NavigationContext";
 
export const useNavigation = () => useContext(NavigationContext);