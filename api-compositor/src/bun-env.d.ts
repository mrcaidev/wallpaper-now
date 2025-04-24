declare module "bun" {
  interface Env {
    WALLPAPER_MANAGER_BASE_URL: string;
    INTERACTION_CONTROLLER_BASE_URL: string;
    RECOMMENDER_BASE_URL: string;
    TRENDING_TRACKER_BASE_URL: string;
  }
}
