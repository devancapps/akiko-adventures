# Akiko Adventures - Travel Affiliate Site

A responsive travel affiliate website featuring flight and hotel deals, powered by Skyscanner and Booking.com.

## Features

- Responsive design with modern UI
- Skyscanner flight search widget
- Booking.com hotel widget
- Blog posts with affiliate links
- Email subscription form
- Popular routes grid
- Firebase hosting ready

## Setup

1. Replace affiliate IDs:
   - Replace `YOUR_ID` in `index.html` with your Skyscanner affiliate ID
   - Replace `YOUR_ID` in `index.html` with your Booking.com affiliate ID
   - Update email subscription form endpoint in `index.html`

2. Add your own images:
   - Replace `/assets/tokyo-hotel-preview.jpg` with your preferred image
   - Add images for blog posts

## Deployment

1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

2. Login to Firebase:
   ```bash
   firebase login
   ```

3. Initialize Firebase project:
   ```bash
   firebase init
   ```

4. Deploy to Firebase:
   ```bash
   firebase deploy
   ```

## Customization

- Update colors in `styles.css` by modifying the CSS variables in `:root`
- Add more blog posts in the `/blog` directory
- Update popular routes in `index.html`
- Modify email subscription form endpoint

## License

MIT License 