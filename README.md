# Akiko Adventures

A modern travel affiliate website built with React, TypeScript, and Tailwind CSS.

## Features

- Modern React application with TypeScript
- Responsive design with Tailwind CSS
- Client-side routing with React Router
- Lazy-loaded components for better performance
- SEO-friendly structure
- Integration with travel affiliate APIs (Skyscanner, Booking.com)

## Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/akiko-adventures.git
   cd akiko-adventures
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── assets/           # Static assets (images, icons)
├── components/       # Reusable UI components
├── layouts/          # Layout components (Header, Footer)
├── pages/            # Page components (Home, Blog)
├── routes/           # Route definitions
├── services/         # API service modules
├── utils/            # Utility functions
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
├── App.tsx           # Root component
└── main.tsx          # Entry point
```

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 